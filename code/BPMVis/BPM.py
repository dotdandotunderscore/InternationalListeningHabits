import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os, time, datetime
from spotipy import *

def get_songs_from_playlists(token, playlist_ids):
    all_song_names = []
    all_song_ids =[]
    for id in playlist_ids:
        tracks = get_tracks_in_playlist(token, id)
        songs = [track["track"] for track in tracks if track != None]
        current_names = [song["name"] for song in songs]
        current_ids = [song["id"] for song in songs]
        num_items = len(current_names)
        if num_items != 50:
            for i in range(50-num_items):
                current_names.append(None)
                current_ids.append(None)
        all_song_names.append(current_names)
        all_song_ids.append(current_ids)
    return all_song_names,all_song_ids
    
def get_audio_features_of_song_ids_from_playlists(token, song_ids):
    all_afs = []
    for ids in song_ids:
        afs = get_audio_features_of_song_ids(token, [id for id in ids if id != None])
        current_afs = [song for song in afs]
        num_items = len(current_afs)
        if num_items != 50:
            for i in range(50-num_items):
                current_afs.append(None)
        all_afs.append(current_afs)
    return all_afs

current_date = datetime.date.today()
token = get_token()

if (os.path.isfile(os.getcwd()+'//code//all_names.npy') and os.path.isfile(os.getcwd()+'//code//all_ids.npy') 
    and os.path.isfile(os.getcwd()+'//code//all_song_names.npy') and os.path.isfile(os.getcwd()+'//code//all_song_ids.npy')
    and os.path.isfile(os.getcwd()+'//code//all_song_afs.npy') and time.time() - os.path.getmtime(os.getcwd()+'//code//all_names.npy') < 18000):
    all_names = np.load(os.getcwd()+'//code//all_names.npy')
    all_ids = np.load(os.getcwd()+'//code//all_ids.npy')
    all_song_names = np.load(os.getcwd()+'//code//all_song_names.npy')
    all_song_ids = np.load(os.getcwd()+'//code//all_song_ids.npy')
else:
    all_names, all_ids = get_spotify_top_50s(token)
    np.save(os.getcwd()+'//code//all_names.npy', all_names)
    np.save(os.getcwd()+'//code//all_ids.npy', all_ids)

    all_song_names, all_song_ids = get_songs_from_playlists(token, all_ids)
    all_afs = get_audio_features_of_song_ids_from_playlists(token, all_song_ids)
    np.save(os.getcwd()+'//code//all_song_names.npy', all_song_names)
    np.save(os.getcwd()+'//code//all_song_ids.npy', all_song_ids)
    np.save(os.getcwd()+'//code//all_afs.npy', all_afs)
    
av_tempos = []
all_tempos = []
for afs in all_afs:
    tempos = [song["tempo"] for song in afs if song != None]
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
    if len([song_name for song_name in sorted_song_names[i] if song_name != None]) != 50:
        num_items = len([song_name for song_name in sorted_song_names[i] if song_name != None])
    else:
        num_items = 50
    df_append = pd.DataFrame({
        "Country": names_list[:num_items],
        "Beats per minute": sorted_all_tempos[i][:num_items],
        "Song name": [song_name for song_name in sorted_song_names[i] if song_name != None]
    })
    all_df = pd.concat([all_df,df_append], ignore_index=True)

fig1 = px.scatter(all_df, x='Country', y='Beats per minute', hover_data=['Country','Beats per minute','Song name'],
                   color='Beats per minute', symbol='Country', title=f'Average BPM of "Top 50" songs per country according to Spotify - Updated {current_date}')
fig2 = px.line(averages_df, x='Country', y='Average BPM')
fig3 = go.Figure(data=fig1.data + fig2.data, layout=fig1.layout)
fig3['layout']['xaxis']['autorange'] = "reversed"
fig3.update_coloraxes(showscale=False)
# fig3.update_layout({
#     'plot_bgcolor': 'rgba(84, 84, 84, 0.8)',
#     'paper_bgcolor': 'rgba(84, 84, 84, 0.8)',
# })
fig3.write_html(os.getcwd()+'//code//BPMVis//BPM.html')
fig3.show()