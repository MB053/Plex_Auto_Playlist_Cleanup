import requests
import xml.etree.ElementTree as ET
import os

# ======= CONFIG =======
PLEX_URL = "http://<YOUR_PLEX_IP>:32400"
PLEX_TOKEN = "<YOUR_PLEX_TOKEN>"

MOVIE_PLAYLIST = "YOUR_FILM_PLAYLIST"
SHOW_PLAYLIST = "YOUR_SHOW_PLAYLIST"

DEBUG = True  # Set to False to reduce output
# ======================

headers = {
    "X-Plex-Token": PLEX_TOKEN
}


def debug(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")


def verify_token():
    url = f"{PLEX_URL}/identity"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("✅ Plex token is valid.")
    else:
        print(f"❌ Invalid Plex token or access denied (status code {response.status_code}).")
        exit(1)


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
        playlist_item_id = (
            playlist_item.attrib.get("ratingKey")
            if playlist_item is not None
            else video.attrib.get("playlistItemID")
        )

        items.append({
            "title": video.attrib.get("title"),
            "view_count": int(video.attrib.get("viewCount", 0)),
            "media_rating_key": video.attrib.get("ratingKey"),
            "playlist_item_id": playlist_item_id,
            "type": video.attrib.get("type"),
            "collection": video.attrib.get("collection", None),
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
    uri = f"library://{rating_key}/item"
    url = f"{PLEX_URL}/playlists/{playlist_id}/items?uri={uri}"
    response = requests.put(url, headers=headers)
    return response.status_code == 200


def get_next_item_in_collection(collection_name, current_index):
    url = f"{PLEX_URL}/library/sections"
    sections = requests.get(url, headers=headers)
    root = ET.fromstring(sections.content)

    section_ids = [s.attrib['key'] for s in root.findall('Directory') if s.attrib.get('type') == 'movie']

    for section_id in section_ids:
        search_url = f"{PLEX_URL}/library/sections/{section_id}/all?collection={collection_name}"
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            continue

        root = ET.fromstring(response.content)
        for video in root.findall("Video"):
            index = int(video.attrib.get("index", 0))
            view_count = int(video.attrib.get("viewCount", 0))
            title = video.attrib.get("title")
            rating_key = video.attrib.get("ratingKey")

            if index == current_index + 1 and view_count == 0:
                return {"title": title, "rating_key": rating_key}

    return None


def get_next_episode(grandparent_key, current_index):
    url = f"{PLEX_URL}/library/metadata/{grandparent_key}/children"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    root = ET.fromstring(response.content)
    for episode in root.findall("Video"):
        index = int(episode.attrib.get("index", 0))
        view_count = int(episode.attrib.get("viewCount", 0))
        if index == current_index + 1 and view_count == 0:
            return {"title": episode.attrib.get("title"), "rating_key": episode.attrib.get("ratingKey")}
    return None


def process_playlist(playlist_name, media_type_filter):
    print(f"\n--- Processing Playlist: {playlist_name} ---")
    playlist_id = get_playlist_id_by_name(playlist_name)
    if not playlist_id:
        print(f"⚠️ Playlist '{playlist_name}' not found.")
        return

    items = get_playlist_items(playlist_id)
    removed = 0

    for item in items:
        if item["type"] != media_type_filter:
            continue

        title = item["title"]
        view_count = item["view_count"]
        playlist_item_id = item["playlist_item_id"]
        collection = item["collection"]
        index = item["index"]
        grandparent_key = item["grandparent_rating_key"]

        debug(f"→ {title}: viewCount = {view_count}")

        if view_count > 0:
            if not playlist_item_id:
                print(f"  ⚠️ No PlaylistItem ID found for: {title} — skipping deletion.")
                continue

            status_code, _ = remove_item_from_playlist(playlist_id, playlist_item_id)
            if status_code == 200:
                print(f"  ✅ Removed: {title}")
                removed += 1

                if collection and item["type"] == "movie":
                    next_item = get_next_item_in_collection(collection, index)
                    if next_item and not is_item_already_in_playlist(items, next_item["rating_key"]):
                        if add_item_to_playlist(playlist_id, next_item["rating_key"]):
                            print(f"    ➕ Added next movie in collection: {next_item['title']}")

                # 🔒 Series logic - currently disabled
                # if item["type"] == "episode":
                #     next_ep = get_next_episode(grandparent_key, index)
                #     if next_ep and not is_item_already_in_playlist(items, next_ep["rating_key"]):
                #         if add_item_to_playlist(playlist_id, next_ep["rating_key"]):
                #             print(f"    ➕ Added next episode: {next_ep['title']}")
            else:
                print(f"  ❌ Failed to remove: {title} (status code {status_code})")
        else:
            debug(f"  ⏭️  Skipped (unwatched): {title}")

    print(f"✔️ Total removed from '{playlist_name}': {removed} item(s).")


def main():
    print(f"Running as user: {os.getenv('USER') or os.getenv('USERNAME')}")
    verify_token()
    process_playlist(MOVIE_PLAYLIST, media_type_filter="movie")
    process_playlist(SHOW_PLAYLIST, media_type_filter="episode")
    # process_watchlist()  # Optional future feature


if __name__ == "__main__":
    main()
