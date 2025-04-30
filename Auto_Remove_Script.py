import requests
import xml.etree.ElementTree as ET
import os
from urllib.parse import quote

# ======= CONFIG =======
PLEX_URL = "http://<YOUR_PLEX_IP>:32400"
PLEX_TOKEN = "<YOUR_PLEX_TOKEN>"

MOVIE_PLAYLIST = "YOUR_FILM_PLAYLIST"
SHOW_PLAYLIST = "YOUR_SHOW_PLAYLIS

DEBUG = True
# ======================

headers = {"X-Plex-Token": PLEX_TOKEN}


def debug(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")


def verify_token():
    url = f"{PLEX_URL}/identity"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("✅ Plex token is valid.")
        global MACHINE_ID
        root = ET.fromstring(response.content)
        MACHINE_ID = root.attrib.get("machineIdentifier")
        debug(f"🔧 Machine ID: {MACHINE_ID}")
    else:
        print(f"❌ Invalid Plex token or access denied (status code {response.status_code}).")
        exit(1)
    root = ET.fromstring(response.content)
    for playlist in root.findall("Playlist"):
        if playlist.attrib.get("title") == name:
            debug(f"Found playlist '{name}' with ID {playlist.attrib.get('ratingKey')}")
            return playlist.attrib.get("ratingKey")
    return None


def get_playlist_id_by_name(name):
    response = requests.get(f"{PLEX_URL}/playlists", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch playlists (status code {response.status_code})")
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
        debug(f"✅ Collection identified from <Collection>: {collection_name}")
        return collection_name

    tags = root.findall(".//Tag[@tagType='1']")
    if tags:
        collection_name = tags[0].attrib.get("tag")
        debug(f"✅ Collection identified from <Tag>: {collection_name}")
        return collection_name

    debug("❌ No collection identified.")
    return None


def get_playlist_items(playlist_id):
    url = f"{PLEX_URL}/playlists/{playlist_id}/items"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch items for playlist {playlist_id} (status code {response.status_code})")
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
            "index": int(video.attrib.get("index", 0)),
            "grandparent_rating_key": video.attrib.get("grandparentRatingKey", "")
        })
    return items


def remove_item_from_playlist(playlist_id, playlist_item_id):
    url = f"{PLEX_URL}/playlists/{playlist_id}/items/{playlist_item_id}"
    response = requests.delete(url, headers=headers)
    return response.status_code, response.text


def is_item_already_in_playlist(playlist_items, rating_key):
    return any(item["media_rating_key"] == rating_key for item in playlist_items)


def add_item_to_playlist(playlist_id, rating_key):
    if not MACHINE_ID:
        debug("❌ MACHINE_ID not set. Cannot add item.")
        return False

    uri = f"server://{MACHINE_ID}/com.plexapp.plugins.library/library/metadata/{rating_key}"
    url = f"{PLEX_URL}/playlists/{playlist_id}/items?uri={quote(uri)}"
    response = requests.put(url, headers=headers)
    if response.status_code != 200:
        debug(f"❌ Add failed (status {response.status_code}): {response.text}")
    return response.status_code == 200


def get_next_item_in_collection(collection_name, current_index_rating_key):
    url = f"{PLEX_URL}/library/sections"
    sections = requests.get(url, headers=headers)
    root = ET.fromstring(sections.content)

    section_ids = [s.attrib['key'] for s in root.findall('Directory') if s.attrib.get('type') == 'movie']

    for section_id in section_ids:
        encoded_collection = quote(collection_name)
        search_url = f"{PLEX_URL}/library/sections/{section_id}/all?collection={encoded_collection}&sort=originallyAvailableAt"
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            continue

        root = ET.fromstring(response.content)
        collection_videos = root.findall("Video")

        found_current = False
        for video in collection_videos:
            title = video.attrib.get("title")
            rating_key = video.attrib.get("ratingKey")
            view_count = int(video.attrib.get("viewCount", 0))

            if found_current and view_count == 0:
                debug(f"Found next in collection: {title}")
                return {"title": title, "rating_key": rating_key}

            if rating_key == current_index_rating_key:
                found_current = True

    debug(f"No next unwatched item found in collection '{collection_name}'")
    return None


def process_playlist(playlist_name, media_type_filter):
    playlist_id = get_playlist_id_by_name(playlist_name)
    if not playlist_id:
        print(f"⚠️ Playlist '{playlist_name}' not found.")
        return

    items = get_playlist_items(playlist_id)
    removed = 0
    added = 0

    for item in items:
        if item["type"] != media_type_filter:
            continue

        title = item["title"]
        view_count = item["view_count"]
        collection = item["collection"]
        index = item["index"]

        if view_count > 0:
            status, _ = remove_item_from_playlist(playlist_id, item["playlist_item_id"])
            if status == 200:
                debug(f"✅ Removed watched item: {title}")
                removed += 1

                if collection:
                    next_item = get_next_item_in_collection(collection, item["media_rating_key"])
                    if next_item:
                        current_items = get_playlist_items(playlist_id)
                        if not is_item_already_in_playlist(current_items, next_item["rating_key"]):
                            debug(f"➡️ Attempting to add next item: {next_item['title']} (key {next_item['rating_key']})")
                            if add_item_to_playlist(playlist_id, next_item["rating_key"]):
                                print(f"➕ Added next movie in '{collection}': {next_item['title']}")
                                added += 1
                            else:
                                print(f"❌ Failed to add: {next_item['title']}")
                        else:
                            debug(f"⏩ Already in playlist: {next_item['title']}")
                    else:
                        debug(f"📭 No next item found in collection: {collection}")
            else:
                print(f"❌ Failed to remove {title}")
        else:
            debug(f"⏭️ Skipping unwatched: {title}")

    print(f"✔️ Finished '{playlist_name}': {removed} removed, {added} added.")


def main():
    verify_token()
    process_playlist(MOVIE_PLAYLIST, "movie")
    process_playlist(SHOW_PLAYLIST, "episode")


if __name__ == "__main__":
    main()
