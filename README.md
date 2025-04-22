# 🎬 Auto Cleanup Script for Plex

Automatically manage your Plex playlists by removing watched items and keeping your playlists fresh — (future) optionally continuing movie collections or TV series.

---

## 🚀 What It Does

- ✅ Removes **watched** movies and episodes from specified Plex playlists
- ✅ Supports **multiple playlists** (e.g., movies and shows)
- ✅ Includes full debug output and safety checks
- ✅ Designed for automation via cron, Tautulli, etc.

---

## 🔧 Setup

### 1. Clone the Repo

```bash
git clone https://github.com/MB053/Plex_Auto_Playlist_Cleanup.git
cd plex-auto-remove
```

### 2. Create a Virtual Environment (recommended)

```bash
python3 -m venv plex_env
source plex_env/bin/activate
pip install requests
```

### 3. Edit the Script

Open `Auto_Remove_Script.py` and set the config at the top:

```python
PLEX_URL = "http://<YOUR_PLEX_IP>:32400"
PLEX_TOKEN = "<YOUR_PLEX_TOKEN>"

MOVIE_PLAYLIST = "YOUR_FILM_PLAYLIST"
SHOW_PLAYLIST = "YOUR_SHOW_PLAYLIST"
```

---

## ▶️ Run the Script

```bash
python Auto_Remove_Script.py
```

Or use the included shell wrapper:

```bash
./run_auto_remove.sh
```

---

## ⚙️ Features in Detail

| Feature | Description |
|--------|-------------|
| 🧼 Remove Watched | Removes any playlist item with `viewCount > 0` |
| 📜 XML Support | Handles both `<PlaylistItem>` and `playlistItemID` attributes |
| 🛡 Safe Skips | Gracefully handles items Plex won't allow to be removed |
| 📈 Debug Mode | Enable `DEBUG = True` for full logs of everything it does |

---

## 🧪 Example Output

```bash
--- Processing Playlist: Film Roulette ---
[DEBUG] → Rocky: viewCount = 1
  ✅ Removed: Rocky

--- Processing Playlist: Serie Roulette ---
[DEBUG] → Episode 1: viewCount = 1
  ✅ Removed: Episode 1
```

---

## 🛠 Planned Features

- 🔄 Add next serie episode to playlist
- 💬 Add next movie in collection to Playlist 

---

## 🧑‍💻 Contributing

Feel free to open issues, suggest features, or submit pull requests! Make sure to test your changes with your own Plex instance before submitting.

---

## 🛡 License

MIT — Free to use, modify, and share. Attribution is appreciated 💛

Like the Script show your appriciation
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/MB053)
