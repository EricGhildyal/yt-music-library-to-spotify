from ytmusicapi import YTMusic
from spotipy import Spotify, util
from os import getenv
from dotenv import load_dotenv

PLAYLIST_ID = "[YOUR_SPOTIFY_PLAYLIST_ID]"

def load_env():
    load_dotenv()

#################
# spotify
#################
class Spotify_client:
    def __init__(self, *args, **kwargs):
        client_id = getenv('SPOTIFY_client_id')
        client_secret = getenv('SPOTIFY_client_secret')
        self.username = getenv('SPOTIFY_username')
        redirect_uri = getenv('SPOTIFY_redirect_uri')
        scope = 'playlist-modify-private'

        # login
        print("Starting Spotify client")
        token = util.prompt_for_user_token(self.username,scope,client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri)
        self.sp_client = Spotify(auth=token)

    def create_playlist(self, playlist_name):
        # print(f'playlist_name: {playlist_name}')
        return self.sp_client.user_playlist_create(user=self.username, name=playlist_name, public=False)

    def search_track(self, search_string):
        # print(f'search_string: {search_string}')
        return self.sp_client.search(search_string, limit=1)

    def add_to_playlist(self, playlist_id, track_ids):
        # print(f'playlist_id: {playlist_id}, track_ids: {track_ids}')
        return self.sp_client.user_playlist_add_tracks(self.username, playlist_id, track_ids)


def main():
    yt = YTMusic('headers_auth.json')
    songs = yt.get_library_songs(limit=9000, order='a_to_z')
    songs.extend(yt.get_library_upload_songs(limit=9000, order='a_to_z'))

    print('loading Spotify')
    spot = Spotify_client()
    cnt = 0
    for track_data in songs:
        try:
            artist = track_data.get('artists')[0]['name']
        except Exception:
            artist = track_data.get('artist')[0]['name']
        title = track_data.get('title')
        album = track_data.get('album')
        if album == None:
            album = ""
        else:
            album = album['name']
        print(f'Searching {artist} {title} {album}')
        cnt += 1
        # search by artist title and album
        search_result = spot.search_track(f'{artist} {title} {album}')
        try:
            track_uri = search_result.get('tracks').get('items')[0].get('uri')
        except Exception:
            print("Index out of range: This track may not exist or was not found. Skipping...")
            try:
                with open('./errored-tracks.log', 'a') as file:
                    file.writelines(f'song: {title} {artist}\n\n')
            except:
                print("Error writing track to errored list.  It most likely has special characters.")
            continue
        # add to new playlist
        print(f'Adding {track_uri} to library')
        spot.add_to_playlist(PLAYLIST_ID, [track_uri])
        print('Song added!')
    print(f"Processed {cnt} songs")

if __name__ == "__main__":
    print("================ GETTING SONGS ================")
    load_env()
    main()
    print("================ DONE ================")