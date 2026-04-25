import customtkinter as ctk
from PIL import Image, ImageTk
import os
import tkinter as tk
from dotenv import load_dotenv
import cairosvg
import io
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables
load_dotenv()

# App settings
APP_WIDTH = 500
APP_HEIGHT = 650

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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
        self.current_mode = "spotify"

        # Setup Spotify
        self.setup_spotify()

        # Set background image directly on window
        self.load_background()

        # Load icons
        icons_path = os.path.join(os.path.dirname(__file__), "../assets/icons")
        self.play_icon = load_icon(os.path.join(icons_path, "play.svg"))
        self.pause_icon = load_icon(os.path.join(icons_path, "pause.svg"))
        self.back_icon = load_icon(os.path.join(icons_path, "back.svg"))
        self.next_icon = load_icon(os.path.join(icons_path, "next.svg"))

        # Build UI
        self.build_ui()

        self.poll_spotify()

    def load_background(self):
        bg_path = os.path.join(os.path.dirname(__file__), "../assets/background.jpg")
        bg_image = Image.open(bg_path).resize((APP_WIDTH, APP_HEIGHT))
        self.bg_photo = ImageTk.PhotoImage(bg_image)

        # Use a label as the background
        self.bg_label = tk.Label(self, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def build_ui(self):
        # Mode switcher
        self.spotify_btn = ctk.CTkButton(
            self, text="Spotify", width=120,
            command=lambda: self.switch_mode("spotify"),
            fg_color="#1DB954", hover_color="#1aa34a"
        )
        self.spotify_btn.place(relx=0.35, y=40, anchor="center")

        self.youtube_btn = ctk.CTkButton(
            self, text="YouTube", width=120,
            command=lambda: self.switch_mode("youtube"),
            fg_color="#333333", hover_color="#444444"
        )
        self.youtube_btn.place(relx=0.65, y=40, anchor="center")

        # Album art placeholder
        self.art_label = ctk.CTkLabel(
            self, text="No Song Playing",
            width=200, height=200,
            fg_color="#1E1E1E", corner_radius=12
        )
        self.art_label.place(relx=0.5, y=220, anchor="center")

        # Song title
        self.title_label = ctk.CTkLabel(
            self, text="Song Title",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white", fg_color="transparent"
        )
        self.title_label.place(relx=0.5, y=350, anchor="center")

        # Artist name
        self.artist_label = ctk.CTkLabel(
            self, text="Artist Name",
            font=ctk.CTkFont(size=14),
            text_color="#AAAAAA", fg_color="transparent"
        )
        self.artist_label.place(relx=0.5, y=380, anchor="center")

        # Progress bar
        self.progress = ctk.CTkSlider(
            self, from_=0, to=100,
            width=300, button_color="white",
            progress_color="white", fg_color="#2A588D",
            bg_color="transparent"
        )
        self.progress.place(relx=0.5, y=420, anchor="center")

        # Back button
        self.back_btn = ctk.CTkButton(
            self, image=self.back_icon, text="",
            width=100, height=100,
            fg_color="transparent", hover_color="#10356B",
            border_width=0, bg_color="#10356B", corner_radius=0,
            command=self.skip_back
        )
        self.back_btn.place(relx=0.3, y=490, anchor="center")

        # Play button
        self.play_btn = ctk.CTkButton(
            self, image=self.play_icon, text="",
            width=60, height=60,
            fg_color="transparent", hover_color="#10356B",
            border_width=0, bg_color="#10356B", corner_radius=0,
            command=self.toggle_play
        )
        self.play_btn.place(relx=0.5, y=490, anchor="center")

        # Next button
        self.next_btn = ctk.CTkButton(
            self, image=self.next_icon, text="",
            width=50, height=50,
            fg_color="transparent", hover_color="#10356B",
            border_width=0, bg_color="#10356B",
            command=self.skip_next
        )
        self.next_btn.place(relx=0.7, y=490, anchor="center")

    def switch_mode(self, mode):
        self.current_mode = mode
        if mode == "spotify":
            self.spotify_btn.configure(fg_color="#1DB954")
            self.youtube_btn.configure(fg_color="#333333")
        else:
            self.spotify_btn.configure(fg_color="#333333")
            self.youtube_btn.configure(fg_color="#FF0000")

    def toggle_play(self):
        try:
            if self.is_playing:
                self.sp.pause_playback()
                self.play_btn.configure(image=self.play_icon)
            else:
                self.sp.start_playback()
                self.play_btn.configure(image=self.pause_icon)
            self.is_playing = not self.is_playing
        except Exception as e:
            print(f"Error toggling play: {e}")

    def skip_back(self):
        try:
            self.sp.previous_track()
        except Exception as e:
            print(f"Error skipping back: {e}")

    def skip_next(self):
        try:
            self.sp.next_track()
        except Exception as e:
            print(f"Error skipping next: {e}")

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

    def update_ui(self, title, artist, art_url, progress, duration):
        # Update labels
        self.title_label.configure(text=title)
        self.artist_label.configure(text=artist)

        # Update progress bar
        self.progress.configure(to=duration)
        self.progress.set(progress)

        # Load album art from URL
        import requests
        from PIL import Image
        import io
        response = requests.get(art_url)
        img = Image.open(io.BytesIO(response.content)).resize((200, 200))
        self.art_photo = ImageTk.PhotoImage(img)
        self.art_label.configure(image=self.art_photo, text="")

    def poll_spotify(self):
        if self.current_mode == "spotify":
            self.get_current_track()
        self.after(3000, self.poll_spotify)

# Run the app
if __name__ == "__main__":
    app = MusicPlayer()
    app.mainloop()