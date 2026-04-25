# Python Music Player

A simple music player interface that connects with your spotify account, built with Python and CustomTkinter.

## Features
- Syncs with your currently playing Spotify track
- Displays album art, song title, and artist
- Play/pause and skip controls
- Real-time progress bar

## Requirements
- Python 3.11+
- Spotify Premium account

## Setup
1. Clone the repo
2. Install dependencies:
   pip3 install -r requirements.txt
3. Create a `.env` file in the root folder:
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
4. Run the app:
   python3 src/main.py

## Built With
- Python
- CustomTkinter
- Spotipy
- Pillow
- CairoSVG