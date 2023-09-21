from requests import post, get
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os, time, base64, json

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
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

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search(token, type_str, name, limit=1):
    url = 'https://api.spotify.com/v1/search/'
    headers = get_auth_header(token)
    query = f"q={name}&type={type_str}&limit={limit}&tag=new"

    query_url = url+"?"+query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)[f"{type_str}s"]["items"]
    if len(json_result) == 0:
        print("None found.")
        return None
    return json_result

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

def get_audio_features_of_songs(token, songs):
    url = "https://api.spotify.com/v1/audio-features"
    headers = get_auth_header(token)
    query = "ids="+",".join([song["id"] for song in songs])

    query_url = url + "?" + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["audio_features"]
    return json_result

def get_users_playlists(token, user_id, limit=50, offset=0):
    url = f"https://api.spotify.com/v1/users/spotify/playlists"
    headers = get_auth_header(token)
    query = f"limit={limit}&offset={offset}"

    query_url = url + "?" + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["items"]
    return json_result

def get_tracks_in_playlist(token, playlist_id, limit=50):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    query = f"fields=items(track(name,id))&limit={limit}"

    query_url = url + "?" + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["items"]
    return json_result

def get_spotify_top_50s(token):
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

token = get_token()

if os.path.isfile(os.getcwd()+'//all_names.npy') and os.path.isfile(os.getcwd()+'//all_ids.npy') and time.time() - os.path.getmtime(os.getcwd()+'//all_names.npy') < 18000:
    all_names = np.load(os.getcwd()+'//all_names.npy')
    all_ids = np.load(os.getcwd()+'//all_ids.npy')
else:
    all_names, all_ids = get_spotify_top_50s(token)
    np.save(os.getcwd()+'//all_names.npy', all_names)
    np.save(os.getcwd()+'//all_ids.npy', all_ids)

av_tempos = []
all_tempos = []
all_song_names = []
for id in all_ids:
    tracks = get_tracks_in_playlist(token, id)
    songs = [track["track"] for track in tracks]
    all_song_names.append([song["name"] for song in songs])
    acoustics = get_audio_features_of_songs(token, songs)
    acoustics = [song for song in acoustics if song != None]
    tempos = [song["tempo"] for song in acoustics]
    if len(tempos) != 50:
        tempos.append(int(np.average(tempos)))
    all_tempos.append(tempos)
    av_tempos.append(np.average(tempos))

sorted_tempos, sorted_names, sorted_all_tempos, sorted_song_names = zip(*sorted(zip(av_tempos, [country[9:] for country in all_names], all_tempos, all_song_names)))

averages_df = pd.DataFrame({
    "Country": sorted_names,
    "Average BPM": sorted_tempos
})

names_list = [sorted_names[0]]*len(sorted_all_tempos[0])
all_df = pd.DataFrame({
    "Country": names_list,
    "Beats per minute": sorted_all_tempos[0],
    "Song name": sorted_song_names[0]
})

for i in range(1,len(sorted_names)):
    names_list = [sorted_names[i]]*len(sorted_all_tempos[i])
    df_append = pd.DataFrame({
        "Country": names_list,
        "Beats per minute": sorted_all_tempos[i],
        "Song name": sorted_song_names[i]
    })
    all_df = pd.concat([all_df,df_append], ignore_index=True)

fig1 = px.scatter(all_df, x='Country', y='Beats per minute', hover_data=['Country','Beats per minute','Song name'],
                   color='Beats per minute', symbol='Country', title='Average BPM of "Top 50" songs per country according to Spotify')
fig2 = px.line(averages_df, x='Country', y='Average BPM')
fig3 = go.Figure(data=fig1.data + fig2.data, layout=fig1.layout)
fig3['layout']['xaxis']['autorange'] = "reversed"
fig3.update_coloraxes(showscale=False)
fig3.write_html(os.getcwd()+'//docs//BPM.html')
fig3.show()