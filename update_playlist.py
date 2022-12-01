import spotipy
import argparse
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import os
from datetime import datetime
from difflib import SequenceMatcher

os.environ["SPOTIPY_CLIENT_ID"] = "7fd22ab7a9a943c79928daf24119f162"
os.environ["SPOTIPY_CLIENT_SECRET"] = "c2bbae41e56141049f3f43513fd7da61"
os.environ["SPOTIPY_REDIRECT_URI"] = "https://localhost:8588/callback"

ARTISTS_FILE = "./failed_artists.txt"
PLAYLIST = "4H6AOPQVZd2TsfV7ploApK"
DATETIME_FORMATS = ["%Y-%m-%d", "%Y-%m", "%Y"]
SIMILARITY_THRESHOLD = 0.75

def get_similarity(str1, str2):
    return SequenceMatcher(None, str1, str2).ratio()

def datestr_to_datetime(datestr):
    for format in DATETIME_FORMATS:
        try:
            return datetime.strptime(datestr, format)
        except:
            continue
    return None

def _get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--playlist", "-p", default=PLAYLIST)
    parser.add_argument("--input-file", "-i", default=ARTISTS_FILE)
    parser.add_argument("--use-similarity", action="store_true", default=True)
    parser.add_argument("--use-start", action="store_true", default=False)
    return parser

def get_unique_albums_by_name(albums):
    seen = []
    unique_albums = []
    for album in albums:
        if album["name"] not in seen:
            seen.append(album["name"])
            unique_albums.append(album)
    return unique_albums

def get_latest_album_id(artist_id, sp):
    results = sp.artist_albums(artist_id)
    albums = results['items']
    albums = [album for album in albums if len(album["artists"]) == 1] # exclude multiple artist albums, ie collabs
    for album in albums:
        datestr = album["release_date"]
        album["release_date_dtm"] = datestr_to_datetime(datestr)
    albums = sorted(albums, key= lambda x: x["release_date_dtm"],
                    reverse=True)
    albums = get_unique_albums_by_name(albums)
    return albums[0]['id']

def get_album_tracks(album_id, sp):
    track_ids = [item["id"] for item in sp.album(album_id)["tracks"]["items"]]
    tracks = [sp.track(id) for id in track_ids]
    tracks = [track for track in tracks if 
                len(track["artists"]) == 1 and track["artists"][0]["name"] != "Various Artists"]
    return tracks

def load_artists(filepath):
    with open(filepath, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def get_artists_names_ids(results):
    names_and_ids = [(artist['name'], artist['id']) for artist in 
                    results["artists"]["items"]]
    return names_and_ids

def get_artist_query(artist):
    # some special characters in artist name can screw up the query. replace these.
    return artist.replace(":", "\:")

def get_artist_id(artist, sp, use_similarity, use_start):
    artist_query = get_artist_query(artist)
    results = sp.search(q=f"artist:{artist_query}", limit=30, type="artist")
    names_and_ids = get_artists_names_ids(results)
    nomatch_info = f"No match for artist {artist}."
    if not names_and_ids:
        return None, nomatch_info
    # first loop: look for exact match
    for i, (name, id) in enumerate(names_and_ids):
        similarity = get_similarity(name, artist)
        names_and_ids[i] = (similarity, name, id)
        if name.lower() == artist.lower():
            return id, ''
    # second loop: check if beginnings of names match
    # ie artist "John Smith" would match with "John Smith Trio"
    for _, name, id in names_and_ids:
        if use_start:
            if name.lower().startswith(artist.lower()):
                info = f"No match for artist {artist}. Choosing best alternative {name}."
                return id, info
    
    # If nothing found, select most similar artist name
    # if similarity is above threshold
    # ie artist "Frank Meissen" would match with "Frank Meißen"
    names_and_ids = sorted(names_and_ids, reverse=True)
    most_similar = names_and_ids[0]
    if most_similar[0] > SIMILARITY_THRESHOLD and use_similarity:
        name = most_similar[1]
        info = f"No match for artist {artist}. Choosing best alternative {name}"
        return most_similar[-1], info
    return None, nomatch_info

def empty_playlist(playlist, sp):
    playlist_items = sp.playlist_items(playlist)['items']
    
    while playlist_items:
        if not isinstance(playlist_items, list):
            return
        track_ids = [item['track']['id'] for item in playlist_items]
        sp.playlist_remove_all_occurrences_of_items(playlist, track_ids)
        playlist_items = sp.playlist_items(playlist)

def main():
    parser = _get_parser()
    args = parser.parse_args()
    scope = "playlist-modify-public"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    
    print("emptying existing playlist...")
    empty_playlist(args.playlist, sp)
    tracks = []
    artists = load_artists(args.input_file)
    infos = []
    for artist in artists:
        try:

            print(f"Processing {artist}")
            artist_id, info = get_artist_id(artist, sp, args.use_similarity,
                                args.use_start)
            infos.append(info)
            if artist_id is None:
                continue
            latest_album_id = get_latest_album_id(artist_id, sp)
            album_tracks = get_album_tracks(latest_album_id, sp)
            album_tracks = sorted(album_tracks, key = lambda x: x["popularity"],
                                    reverse=True)
            latest_album_top_track = album_tracks[0]
            if latest_album_top_track["id"] == "5ebk0kx4g0iB3xXyW7g1a1":
                print("DEBUG")
            tracks.append(latest_album_top_track["id"])
        except Exception as e:
            infos.append(f"Error processing {artist}: {e}")
            print(f"Error processing {artist}: {e}")


    print("Add new tracks...")
    for i in range(0,len(tracks), 100):
        end = min(len(tracks), i + 100)
        sp.playlist_add_items(args.playlist, tracks[i:end])
    print("Done!")

    print("\n\n")
    print("\n".join([info for info in infos if info]))

if __name__ == '__main__':
    main()
