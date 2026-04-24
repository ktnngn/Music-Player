import customtkinter as ctk
from PIL import Image, ImageTk
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App settings
APP_WIDTH = 400
APP_HEIGHT = 650

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MusicPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Music Player")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.resizable(False, False)

        # Load and set background
        self.load_background()

    def load_background(self):
        # Load your background image
        bg_path = os.path.join(os.path.dirname(__file__), "../assets/background.jpg")
        bg_image = Image.open(bg_path).resize((APP_WIDTH, APP_HEIGHT))
        self.bg_photo = ImageTk.PhotoImage(bg_image)

        # Create canvas to hold background
        self.canvas = ctk.CTkCanvas(self, width=APP_WIDTH, height=APP_HEIGHT)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

# Run the app
if __name__ == "__main__":
    app = MusicPlayer()
    app.mainloop()