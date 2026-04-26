# Python Music Player

![Music Player Screenshot](screenshots/screenshot.png)
A simple music player interface that connects with your spotify account, built with Python and CustomTkinter.

## Features
- Syncs with your currently playing Spotify track in real time
- Displays album art, song title, and artist name
- Play/pause and skip controls
- Real-time progress bar with timestamps
- Built for Mac and Windows

## Requirements
- Spotify Premium account
- Spotify Developer API keys

## Download
Download the latest build from the [Actions tab](https://github.com/ktnngn/Music-Player/actions) under Artifacts.

## Run from source
1. Clone the repo
2. Install dependencies:
   pip3 install -r requirements.txt
3. Create a `.env` file in the root folder:
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
4. Run:
   python3 src/main.py

## Built With
- Python 3.11
- CustomTkinter
- Spotipy
- Pillow
- CairoSVG
- GitHub Actions (CI/CD)