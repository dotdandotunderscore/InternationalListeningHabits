from dotenv import load_dotenv
from requests import post, get
import numpy as np
import os, base64, json

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    ''' Produces an authorisation token from a Spotify App ID'''
    auth_string = client_id + ':' + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type":"client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def search(token, type_str, name, limit=1):
    '''Search for an object type'''
    url = 'https://api.spotify.com/v1/search/'
    headers = {"Authorization": "Bearer " + token}
    query = f"q={name}&type={type_str}&limit={limit}&tag=new"

    query_url = url+"?"+query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)[f"{type_str}s"]["items"]
    if len(json_result) == 0:
        print("None found.")
        return None
    return json_result

def get_songs_by_artist(token, artist_id):
    ''' Get json of all tracks by an Artist ID'''
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = {"Authorization": "Bearer " + token}

    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

def get_audio_features_of_songs(token, songs):
    ''' Get json of acoustic features of Songs calculated by Spotify API'''
    url = "https://api.spotify.com/v1/audio-features"
    headers = {"Authorization": "Bearer " + token}
    query = "ids="+",".join([song["id"] for song in songs])

    query_url = url + "?" + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["audio_features"]
    return json_result

def get_audio_features_of_song_ids(token, song_ids):
    ''' Get json of acoustic features of Song IDs calculated by Spotify API'''
    url = "https://api.spotify.com/v1/audio-features"
    headers = {"Authorization": "Bearer " + token}
    query = "ids="+",".join(song_ids)

    query_url = url + "?" + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["audio_features"]
    return json_result

def get_users_playlists(token, user_id, limit=50, offset=0):
    '''Get json of playlists owned by a User ID'''
    url = f"https://api.spotify.com/v1/users/spotify/playlists"
    headers = {"Authorization": "Bearer " + token}
    query = f"limit={limit}&offset={offset}"

    query_url = url + "?" + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["items"]
    return json_result

def get_tracks_in_playlist(token, playlist_id, limit=50):
    '''Get json of all tracks in a Playlist ID'''
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": "Bearer " + token}
    query = f"fields=items(track(name,id))&limit={limit}"

    query_url = url + "?" + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["items"]
    return json_result

def get_spotify_top_50s(token):
    '''Gets all Official Spotify playlist names and IDs'''
    idx = 0
    all_names = []
    all_ids = []
    playlists = [0]

    while len(playlists) != 0:
        playlists = get_users_playlists(token, "spotify", offset=idx*50)
        names = [playlist["name"] for playlist in playlists]
        ids = [playlist["id"] for playlist in playlists]
        all_names += names
        all_ids += ids
        idx+=1

    all_names = np.array(all_names)
    all_ids = np.array(all_ids)

    top_lists = [playlist[:9] == 'Top 50 - ' for playlist in all_names]
    return all_names[top_lists], all_ids[top_lists]