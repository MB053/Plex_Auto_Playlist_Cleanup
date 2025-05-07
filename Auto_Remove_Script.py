
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

# ======= CONFIG =======
PLEX_URL = "http://<YOUR_PLEX_IP>:32400"
PLEX_TOKEN = "<YOUR_PLEX_TOKEN>"

MOVIE_PLAYLIST = "YOUR_FILM_PLAYLIST"
SHOW_PLAYLIST = "YOUR_SHOW_PLAYLIST"

TELEGRAM_BOT_TOKEN = "<YOUR_TELEGRAM_BOT_TOKEN>"
TELEGRAM_CHAT_ID = "<YOUR_TELEGRAM_CHAT_ID>"

DEBUG = True
# ======================

headers = {"X-Plex-Token": PLEX_TOKEN}
MACHINE_ID = None
telegram_messages = []

def debug(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

def telegram_log(msg):
    telegram_messages.append(msg)
    debug(msg)

def send_telegram_summary():
    if not telegram_messages:
        return
    message = "\n".join(telegram_messages)
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            debug("📢 Telegram summary sent.")
        else:
            debug(f"❌ Telegram failed: {response.text}")

def verify_token():
    url = f"{PLEX_URL}/identity"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        global MACHINE_ID
        root = ET.fromstring(response.content)
        MACHINE_ID = root.attrib.get("machineIdentifier")
        debug("✅ Plex token valid.")
    else:
        exit("❌ Invalid Plex token.")

def get_playlist_id_by_name(name):
    response = requests.get(f"{PLEX_URL}/playlists", headers=headers)
    if response.status_code != 200:
        debug(f"❌ Failed to fetch playlists (status code {response.status_code})")
        return None
    root = ET.fromstring(response.content)
    for playlist in root.findall("Playlist"):
        if playlist.attrib.get("title") == name:
            debug(f"Found playlist '{name}' with ID {playlist.attrib.get('ratingKey')}")
            return playlist.attrib.get("ratingKey")
    return None

def get_collection_name_for_item(rating_key):
    url = f"{PLEX_URL}/library/metadata/{rating_key}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        debug(f"❌ Failed to fetch metadata for ratingKey {rating_key}")
        return None
    root = ET.fromstring(response.content)
    collections = root.findall(".//Collection")
    if collections:
        collection_name = collections[0].attrib.get("tag")
        debug(f"✅ Collection identified: {collection_name}")
        return collection_name
    tags = root.findall(".//Tag[@tagType='1']")
    if tags:
        collection_name = tags[0].attrib.get("tag")
        debug(f"✅ Collection identified via tag: {collection_name}")
        return collection_name
    debug("❌ No collection identified.")
    return None

def get_playlist_items(playlist_id):
    url = f"{PLEX_URL}/playlists/{playlist_id}/items"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        debug(f"❌ Failed to fetch playlist items (status {response.status_code})")
        return []
    root = ET.fromstring(response.content)
    items = []
    for video in root.findall("Video"):
        playlist_item = video.find("PlaylistItem")
        playlist_item_id = playlist_item.attrib.get("ratingKey") if playlist_item is not None else video.attrib.get("playlistItemID")
        rating_key = video.attrib.get("ratingKey")
        collection = get_collection_name_for_item(rating_key)
        items.append({
            "title": video.attrib.get("title"),
            "view_count": int(video.attrib.get("viewCount", 0)),
            "media_rating_key": rating_key,
            "playlist_item_id": playlist_item_id,
            "type": video.attrib.get("type"),
            "collection": collection,
        })
    return items

def remove_item_from_playlist(playlist_id, playlist_item_id):
    url = f"{PLEX_URL}/playlists/{playlist_id}/items/{playlist_item_id}"
    response = requests.delete(url, headers=headers)
    debug(f"Removed playlist item {playlist_item_id} (status {response.status_code})")
    return response.status_code

def is_item_already_in_playlist(playlist_items, rating_key):
    exists = any(item["media_rating_key"] == rating_key for item in playlist_items)
    debug(f"Already in playlist: {exists}")
    return exists

def add_item_to_playlist(playlist_id, rating_key):
    if not MACHINE_ID:
        debug("❌ MACHINE_ID not set.")
        return False
    uri = f"server://{MACHINE_ID}/com.plexapp.plugins.library/library/metadata/{rating_key}"
    url = f"{PLEX_URL}/playlists/{playlist_id}/items?uri={quote(uri)}"
    response = requests.put(url, headers=headers)
    debug(f"Add item result (status {response.status_code})")
    return response.status_code == 200

def get_collection_items_sorted(collection_name):
    url = f"{PLEX_URL}/library/sections"
    sections = requests.get(url, headers=headers)
    root = ET.fromstring(sections.content)
    for s in root.findall('Directory'):
        if s.attrib.get('type') == 'movie':
            sec = s.attrib.get('key')
            url = f"{PLEX_URL}/library/sections/{sec}/all?collection={quote(collection_name)}&sort=originallyAvailableAt"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return ET.fromstring(response.content).findall("Video")
    return []

def get_previous_unwatched(collection_name, current_rating_key):
    videos = get_collection_items_sorted(collection_name)
    previous = None
    for video in videos:
        rating_key = video.attrib.get("ratingKey")
        view_count = int(video.attrib.get("viewCount", 0))
        title = video.attrib.get("title")
        if rating_key == current_rating_key:
            if previous and previous["view_count"] == 0:
                debug(f"Found previous unwatched: {previous['title']}")
                return previous
            debug("No previous unwatched found.")
            return None
        previous = {"title": title, "rating_key": rating_key, "view_count": view_count}
    return None

def get_next_unwatched(collection_name, current_rating_key):
    videos = get_collection_items_sorted(collection_name)
    found = False
    for video in videos:
        rating_key = video.attrib.get("ratingKey")
        view_count = int(video.attrib.get("viewCount", 0))
        title = video.attrib.get("title")
        if found and view_count == 0:
            debug(f"Found next unwatched: {title}")
            return {"title": title, "rating_key": rating_key}
        if rating_key == current_rating_key:
            found = True
    debug("No next unwatched found.")
    return None

def process_playlist(playlist_name, media_type_filter):
    playlist_id = get_playlist_id_by_name(playlist_name)
    if not playlist_id:
        return

    items = get_playlist_items(playlist_id)
    for item in items:
        if item["type"] != media_type_filter:
            continue

        title = item["title"]
        collection = item["collection"]
        rating_key = item["media_rating_key"]

        if collection:
            previous = get_previous_unwatched(collection, rating_key)
            if previous:
                if remove_item_from_playlist(playlist_id, item["playlist_item_id"]) == 200:
                    telegram_log(f"🗑 Removed '{title}' → Previous movie '{previous['title']}' is unwatched.")
                    add_item_to_playlist(playlist_id, previous["rating_key"])
                    telegram_log(f"➕ Added previous '{previous['title']}' from '{collection}'.")
                continue

        if item["view_count"] > 0:
            if remove_item_from_playlist(playlist_id, item["playlist_item_id"]) == 200:
                telegram_log(f"🗑 Removed watched '{title}' from playlist.")
                if collection:
                    next_movie = get_next_unwatched(collection, rating_key)
                    if next_movie:
                        add_item_to_playlist(playlist_id, next_movie["rating_key"])
                        telegram_log(f"➕ Added next '{next_movie['title']}' from '{collection}'.")

def main():
    verify_token()
    process_playlist(MOVIE_PLAYLIST, "movie")
    process_playlist(SHOW_PLAYLIST, "episode")
    send_telegram_summary()

if __name__ == "__main__":
    main()
