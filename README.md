🎬 Plex Auto-Clean Playlist Script

This Python script is designed to maintain your Plex playlists by automatically removing watched items and, if applicable, adding the next unwatched item in a movie collection.

It's ideal for users who want their movie or TV show playlists to always contain only unwatched content — and in the right order.

✨ Features

✅ Validates your Plex Token

🧹 Automatically removes watched movies or episodes from specified playlists

🔗 Detects if a movie is part of a Plex Collection and automatically adds the next unwatched movie

🔍 Uses originallyAvailableAt to determine order (instead of relying on unreliable indexes)

📺 Skips this behavior for TV episodes (optional logic)

🔐 Works securely using your Plex Token and server machine ID

🪵 Includes debug output for easy tracking and troubleshooting

📦 Requirements

Python 3.6+

Plex Media Server (local network or remote access)

A valid Plex token

Install required libraries:

pip install requests

⚙️ Configuration

Edit the top of the script:

PLEX_URL = "http://192.168.1.x:32400"
PLEX_TOKEN = "your_plex_token_here"
MOVIE_PLAYLIST = "Film Test"
SHOW_PLAYLIST = "Serie Test"
DEBUG = True  # Set to False to disable debug output

You must create playlists in Plex manually and name them exactly as configured.

🚀 Usage

You can run the script manually:

python plex_playlist_cleaner.py

Or, for automated execution, integrate it into Tautulli as a Notifier script.

🧠 How it works

For Movies

The script checks if a movie in your playlist has been watched.

If it has:

It removes it from the playlist.

If it belongs to a Collection (like "Harry Potter Collection"):

It finds the next unwatched movie in that collection.

It adds it to the playlist.

For TV Shows

Watched episodes are removed.

No episodes are added automatically. (This logic can be extended.)

📂 Example Output

✅ Plex token is valid.
[DEBUG] Found playlist 'Film Test' with ID 31740
[DEBUG] ✅ Removed watched item: Bad Boys
[DEBUG] Found next in collection: Bad Boys for Life
➕ Added next movie in 'Bad Boys Collection': Bad Boys for Life

🔐 Security

Make sure your script is stored safely — your Plex Token provides full access to your server.
Consider using environment variables or secrets management if integrating into larger systems.

🛠️ To-Do / Ideas



📄 License

MIT — feel free to fork, improve, and contribute!

🙏 Credits

Built for Plex enthusiasts who want a "smart" playlist system.

Inspired by the limitations of native Plex playlist behavior.

Happy streaming! 🍿

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/MB053)
