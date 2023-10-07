from __future__ import unicode_literals
from googleapiclient.discovery import build
from dotenv import load_dotenv
from pathlib import Path
import youtube_dl 
import requests
import base64
import json
import csv
import sys
import os
import io

load_dotenv()

cliend_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

GET_PLAYLIST_ITEMS_URL = None
SPOTIFY_TOKEN = None


def main(spotify_id):
    """
    Requires two files, namely playlist.csv and downloaded.csv and their respecive file paths
    """
    print(spotify_id)
    global SPOTIFY_TOKEN 
    SPOTIFY_TOKEN = get_token()
    get_id(spotify_id)

    test = get_playlist()

    # Writes to playlist.csv file the artist and song name from api response
    with open("C:\SpotifyProject\SpotifyDownload\playlist.csv", "w+", newline="") as file:
        if is_file_empty("C:\SpotifyProject\SpotifyDownload\playlist.csv"): 
            file.write("name,artist\n")
        writer = csv.DictWriter(file, fieldnames=["name", "artist"])
        for item in test["items"]:
            writer.writerow({"artist": item["track"]["artists"][0]["name"], "name": item["track"]["name"]})


    search_prompt = [] # Used to store the search promps to use to download in youtube
    downloaded = [] # Used to store the already downloaded songs from downloaded.csv, used to check if song in playlist.csv already in downloaded list
    not_yet_downloaded = [] # Used to store the songs not yet downloaded, used to store the songs in here to sort them first before writing to downloaded.csv
    
    # Gets all songs from downloaded.csv and put into downloaded list
    # Gets songs from playlist.csv and checks if it is already in downloaded list, if not, append to search_prompt list
    with open("C:\SpotifyProject\SpotifyDownload\playlist.csv", "r") as file, open("C:\SpotifyProject\SpotifyDownload\downloaded.csv","r+",newline="") as file2:
        reader = csv.DictReader(file)
        reader2 = csv.reader(file2)
        writer = csv.writer(file2)
        for item in reader2:
            downloaded.append(f"{item[0]},{item[1]}")

        for row in reader:
            name = row["name"]
            artist = row["artist"]
            song = f"{name} by {artist}"
            if f"{name},{artist}" not in downloaded:
                not_yet_downloaded.append([name,artist])
                search_prompt.append(song)
        for song in sorted(not_yet_downloaded):
            writer.writerow(song)

    for num in get_youtube_link_and_download(search_prompt):
        yield num




def get_token():
    """
        Gets authentication details to access Spotify API
    """
    auth_string = f"{cliend_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }

    result = requests.post(url, headers = headers, data = data)
    result_json = result.json()
    token = result_json["access_token"]
    return token


def get_playlist():
    response = requests.get(
        GET_PLAYLIST_ITEMS_URL,
        headers = {
            "Authorization": f"Bearer {SPOTIFY_TOKEN}",
            "Content-Type": "application/json"
        }
    )
    response_json = response.json()
    print(response)
    return response_json




def get_id(spotify_id):
    global GET_PLAYLIST_ITEMS_URL
    GET_PLAYLIST_ITEMS_URL = f"https://api.spotify.com/v1/playlists/{spotify_id}/tracks?fields=items(track(name%2Chref%2Calbum(name%2Chref%2C)%2C%20artists(name)))&limit=10&offset=0"




def get_youtube_link_and_download(song_details: list):
    try:
        progress = 1 / len(song_details) # Defines how much progress bar moves per one song downloaded back in CTk
        downloading = 1 # Defines current number song being downloaded back in CTk

        youtube = build('youtube','v3',developerKey = YOUTUBE_API_KEY)
        for line in song_details:
            request = youtube.search().list(
                part="snippet",
                maxResults=1,
                q=f"{line}",
                safeSearch = "none"
            )

            response = request.execute()

            for item in response:
                if item == "items":
                    for song in response[item]:
                        yield (progress, f"Downloading {downloading} of {len(song_details)}")
                        downloading += 1
                        download_mp3(song["id"]["videoId"])
    except ZeroDivisionError:
        return(1,0)




def download_mp3(video_id: str):
    # Enter the URL of the YouTube video you want to download
    url = f"https://www.youtube.com/watch?v={video_id}"

    # Set the options to download only the audio in mp3 formatfydl
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'C:\\Users\\Genesis Dumallay\\Music\\%(title)s.%(exts)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    try:
        # Create a YoutubeDL object
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except:
        raise RuntimeError("Error with youtube_dl object: see download_mp3 function")




def is_file_empty(path):
    file_path = Path(path)

    if not os.path.getsize(file_path) > 0:
        return True
    return False

