import customtkinter as ctk
from PIL import Image, ImageTk
import os
import tkinter as tk
from dotenv import load_dotenv
import cairosvg
import io
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import sys

# Load environment variables
load_dotenv()

# App settings
APP_WIDTH = 500
APP_HEIGHT = 650

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), '..', relative_path)

def load_icon(path, size=(100, 100)):
    png_data = cairosvg.svg2png(url=path, output_width=size[0], output_height=size[1])
    img = Image.open(io.BytesIO(png_data)).convert("RGBA")
    return ImageTk.PhotoImage(img)

class MusicPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Music Player")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.resizable(False, False)

        # State
        self.is_playing = False
        self.current_progress_ms = 0
        self.timer_id = None

        # Setup Spotify
        self.setup_spotify()

        # Set background image directly on window
        self.load_background()

        # Load icons
        icons_path = resource_path("assets/icons")
        self.play_icon = load_icon(os.path.join(icons_path, "play.svg"))
        self.pause_icon = load_icon(os.path.join(icons_path, "pause.svg"))
        self.back_icon = load_icon(os.path.join(icons_path, "back.svg"))
        self.next_icon = load_icon(os.path.join(icons_path, "next.svg"))

        # Build UI
        self.build_ui()

        # Start progress timer and Spotify polling
        self.start_progress_timer()
        self.poll_spotify()

    def load_background(self):
        bg_path = resource_path("assets/background.jpg")
        bg_image = Image.open(bg_path).resize((APP_WIDTH, APP_HEIGHT))
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        self.bg_label = tk.Label(self, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def build_ui(self):
        # Album art
        self.art_label = tk.Label(
            self,
            bg="#10356B",
            width=300, height=300,
        )
        self.art_label.place(relx=0.5, y=220, anchor="center")

        # Create gray placeholder for album art
        placeholder = Image.new('RGB', (300, 300), color='#1E1E1E')
        self.placeholder_photo = ImageTk.PhotoImage(placeholder)
        self.art_label.configure(image=self.placeholder_photo)
        self.art_label.image = self.placeholder_photo

        # Add label for placeholder
        self.placeholder_text = ctk.CTkLabel(
            self, text="Play a song to start!",
            font=ctk.CTkFont(size=14),
            text_color="#AAAAAA", fg_color="transparent",
            bg_color="#1E1E1E"
        )
        self.placeholder_text.place(relx=0.5, y=220, anchor="center")

        # Song title
        self.title_label = ctk.CTkLabel(
            self, text="Song Title",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white", fg_color="transparent", bg_color="#10356B"
        )
        self.title_label.place(relx=0.5, y=390, anchor="center")

        # Artist name
        self.artist_label = ctk.CTkLabel(
            self, text="Artist Name",
            font=ctk.CTkFont(size=14),
            text_color="#AAAAAA", fg_color="transparent", bg_color="#10356B"
        )
        self.artist_label.place(relx=0.5, y=420, anchor="center")

        # Progress bar
        self.progress = ctk.CTkSlider(
            self, from_=0, to=100,
            width=330, button_color="white",
            progress_color="white", fg_color="#2A588D",
            bg_color="#10356B"
        )
        self.progress.place(relx=0.5, y=460, anchor="center")

        # Timestamps
        self.time_current = ctk.CTkLabel(
            self, text="0:00",
            font=ctk.CTkFont(size=12),
            text_color="#AAAAAA", fg_color="transparent",
            bg_color="#10356B"
        )
        self.time_current.place(relx=0.15, y=470, anchor="center")

        self.time_total = ctk.CTkLabel(
            self, text="0:00",
            font=ctk.CTkFont(size=12),
            text_color="#AAAAAA", fg_color="transparent",
            bg_color="#10356B"
        )
        self.time_total.place(relx=0.85, y=470, anchor="center")

        # Back button
        self.back_btn = ctk.CTkButton(
            self, image=self.back_icon, text="",
            width=100, height=100,
            fg_color="transparent", hover_color="#10356B",
            border_width=0, bg_color="#10356B", corner_radius=0,
            command=self.skip_back
        )
        self.back_btn.place(relx=0.3, y=560, anchor="center")

        # Play button
        self.play_btn = ctk.CTkButton(
            self, image=self.play_icon, text="",
            width=60, height=60,
            fg_color="transparent", hover_color="#10356B",
            border_width=0, bg_color="#10356B", corner_radius=0,
            command=self.toggle_play
        )
        self.play_btn.place(relx=0.5, y=560, anchor="center")

        # Next button
        self.next_btn = ctk.CTkButton(
            self, image=self.next_icon, text="",
            width=50, height=50,
            fg_color="transparent", hover_color="#10356B",
            border_width=0, bg_color="#10356B",
            command=self.skip_next
        )
        self.next_btn.place(relx=0.7, y=560, anchor="center")

    def setup_spotify(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            scope="user-read-playback-state user-modify-playback-state user-read-currently-playing"
        ))

    def get_current_track(self):
        try:
            track = self.sp.current_playback()
            if track and track['is_playing']:
                song = track['item']
                title = song['name']
                artist = song['artists'][0]['name']
                art_url = song['album']['images'][0]['url']
                duration = song['duration_ms']
                progress = track['progress_ms']
                self.update_ui(title, artist, art_url, progress, duration)
                self.is_playing = track['is_playing']
                if self.is_playing:
                    self.play_btn.configure(image=self.pause_icon)
                else:
                    self.play_btn.configure(image=self.play_icon)
        except Exception as e:
            print(f"Error getting track: {e}")

    def start_progress_timer(self):
        if self.is_playing:
            self.current_progress_ms += 1000
            self.progress.set(self.current_progress_ms)
            self.time_current.configure(text=self.ms_to_time(self.current_progress_ms))
        self.timer_id = self.after(1000, self.start_progress_timer)

    def update_ui(self, title, artist, art_url, progress, duration):
        self.title_label.configure(text=title)
        self.artist_label.configure(text=artist)
        self.progress.configure(to=duration)
        self.current_progress_ms = progress
        response = requests.get(art_url)
        img = Image.open(io.BytesIO(response.content)).resize((300, 300))
        self.art_photo = ImageTk.PhotoImage(img)
        self.art_label.configure(image=self.art_photo)
        self.art_label.image = self.art_photo  
        self.time_total.configure(text=self.ms_to_time(duration)) 
        self.placeholder_text.place_forget()

    def ms_to_time(self, ms):
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"

    def toggle_play(self):
        try:
            if self.is_playing:
                self.sp.pause_playback()
                self.play_btn.configure(image=self.play_icon)
                # Stop the timer
                if self.timer_id:
                    self.after_cancel(self.timer_id)
                    self.timer_id = None
            else:
                self.sp.start_playback()
                self.play_btn.configure(image=self.pause_icon)
                # Resume the timer
                self.start_progress_timer()
            self.is_playing = not self.is_playing
        except Exception as e:
            print(f"Error toggling play: {e}")

    def skip_back(self):
        try:
            self.sp.previous_track()
            self.current_progress_ms = 0
            self.progress.set(0)
            self.time_current.configure(text="0:00")
        except Exception as e:
            print(f"Error skipping back: {e}")

    def skip_next(self):
        try:
            self.sp.next_track()
            self.current_progress_ms = 0
            self.progress.set(0)
            self.time_current.configure(text="0:00")
        except Exception as e:
            print(f"Error skipping next: {e}")


    def poll_spotify(self):
        self.get_current_track()
        self.after(3000, self.poll_spotify)

# Run the app
if __name__ == "__main__":
    app = MusicPlayer()
    app.mainloop()