from tkinter import *
from customtkinter import *
from SpotifyDownload.Spotify import *

set_appearance_mode("Dark")
set_default_color_theme("dark-blue")

class download_frame:  
    def __init__(self, window, spotify_id):
        self.local_window = window
        self.local_spotify_id = spotify_id
        self.new_frame = CTkFrame(window)
        self.new_frame.pack(pady=(50,0))

        self.progress_bar = CTkProgressBar(self.new_frame, width = 180)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(25,15), padx=(20))

        self.download_progress = StringVar()
        self.download_label = CTkLabel(self.new_frame, textvariable = self.download_progress)
        self.download_label.pack()

        self.new_button = CTkButton(self.new_frame, text = "Return", corner_radius=8, fg_color=("Black", "#359638"), hover_color=("Black", "#2a7a2f"), command=self.return_main)
        self.new_button.pack(pady=(35,25))

        self.download_songs()

        self.download_progress.set("Download Finished")

    def download_songs(self):
        self.new_button.configure(state = "disabled")
        self.new_frame.update_idletasks()
        progress = 0
    
        for downloaded_progress, in_download in main(self.local_spotify_id.strip()):
            progress += downloaded_progress
            self.download_progress.set(in_download)
            self.progress_bar.set(progress)
            self.progress_bar.update_idletasks()

        self.new_button.configure(state = "normal")

    def return_main(self):
        self.new_frame.destroy()
        main_frame(self.local_window)



#Creates entry frame, upon click of button destroys current page and creates new download frame
class main_frame:
    def __init__(self, window):
        self.local_window = window
        self.frame = CTkFrame(self.local_window)
        self.frame.pack(pady=(40,0))

        self.entry = CTkEntry(self.frame, font=("Arial", 15), placeholder_text="Spotify ID", width=220)
        self.entry.pack(padx=25, pady=(35,0))

        self.button = CTkButton(self.frame, text = "Enter", corner_radius=8, fg_color=("Black", "#359638"), hover_color=("Black", "#2a7a2f"), command=self.download)
        self.button.pack(pady=(35,25))


    def download(self):
        self.spotify_id = self.entry.get()
        self.frame.destroy()
        self.local_window.update()
        new_frame = download_frame(self.local_window, self.spotify_id)



class main_window:
    def __init__(self):
        self.window = CTk()
        self.window.geometry("400x320")
        self.window.title('Spotify Playlist Downloader')
        main_frame(self.window)
        self.window.mainloop()



def main_win():
    window = main_window()


if __name__ == "__main__":
    main_win()
