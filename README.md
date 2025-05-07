
# Plex Auto Playlist Cleaner & Organizer (Ultimate Edition)

Automatically keeps your Plex playlists clean and in proper order by:
- Removing watched movies/shows
- Automatically adding the next or previous unwatched movie from the same collection
- Sending Telegram notifications about all changes
- Optional debug mode for detailed logging

## 📦 Features

✅ Remove watched movies and episodes from playlists.  
✅ Automatically add the next unwatched movie/episode from the same collection.  
✅ Automatically replace movies with their previous movie if the previous is unwatched.  
✅ Telegram notifications with added and removed items (optional).  
✅ Debug mode (optional) for verbose logging during processing.

## 📌 Supported

- Movies (with collection awareness)
- TV Shows (optional, basic)
- Telegram for notification
- Plex API integration

---

## 🚀 Installation

### 1. Download the script

Clone or download this repository or save the script locally.

### 2. Edit configuration

At the top of the script, configure your Plex and Telegram details:

```
PLEX_URL = "http://<YOUR_PLEX_IP>:32400"
PLEX_TOKEN = "<YOUR_PLEX_TOKEN>"

MOVIE_PLAYLIST = "Your Movie Playlist Name"
SHOW_PLAYLIST = "Your Show Playlist Name"

TELEGRAM_BOT_TOKEN = "<YOUR_TELEGRAM_BOT_TOKEN>"
TELEGRAM_CHAT_ID = "<YOUR_TELEGRAM_CHAT_ID>"

DEBUG = True  # Enable or disable detailed debug output
```

- Telegram is optional, leave `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` empty if you do not want notifications.
- Debug mode shows detailed internal processing and is useful for troubleshooting.

### 3. Run the script

```
python3 Auto_Remove_Script_Ultimate_With_Telegram_Debug.py
```

### 4. (Optional) Schedule it with cron

Example crontab entry to run every night at 3am:

```
0 3 * * * /usr/bin/python3 /path/to/Auto_Remove_Script_Ultimate_With_Telegram_Debug.py
```

---

## 🔔 Telegram Notifications

You will receive messages like this on Telegram (if configured):

```
🗑 Removed 'Rocky 3' → Previous movie 'Rocky 2' is unwatched.
➕ Added previous 'Rocky 2' from 'Rocky Collection'.
🗑 Removed watched 'F9' from playlist.
➕ Added next 'Fast X' from 'Fast and the Furious Collection'.
```

### How to get Telegram Bot Token and Chat ID
1. Create a bot via [BotFather](https://t.me/botfather).
2. Send `/start` to the bot and grab your `chat_id` via a simple API call (or use @userinfobot).
3. Fill in `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in the script.

---

## ⚙️ Advanced Options

- Toggle `DEBUG` to `True` or `False` to show verbose debug logs in console.
- Telegram will only show summary notifications (not debug spam).

---

## 📚 Credits

Built and improved step-by-step with feedback and usage cases by @yournamehere + ChatGPT (OpenAI) for advanced scripting support.

---

## 📌 Disclaimer

This script is provided as-is and tested on Plex Media Server latest versions.  
Always test carefully before enabling automated removals on live playlists.


[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/MB053)
