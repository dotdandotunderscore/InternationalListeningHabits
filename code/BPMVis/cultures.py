import numpy as np
import pandas as pd
import datetime, time
from spotipy import *

current_date = datetime.date.today()
token = get_token()

if (os.path.isfile(os.getcwd()+'//all_names.npy') and os.path.isfile(os.getcwd()+'//all_ids.npy') 
    and os.path.isfile(os.getcwd()+'//all_song_names.npy') and os.path.isfile(os.getcwd()+'//all_song_ids.npy')
    and time.time() - os.path.getmtime(os.getcwd()+'//all_names.npy') < 18000):
    all_names = np.load(os.getcwd()+'//all_names.npy')
    all_ids = np.load(os.getcwd()+'//all_ids.npy')
    all_song_names = np.load(os.getcwd()+'//all_song_names.npy')
    all_song_ids = np.load(os.getcwd()+'//all_song_ids.npy')
else:
    all_names, all_ids = get_spotify_top_50s(token)
    np.save(os.getcwd()+'//all_names.npy', all_names)
    np.save(os.getcwd()+'//all_ids.npy', all_ids)



av_tempos = []
all_tempos = []
all_song_names = []
all_song_ids =[]
for id in all_ids:
    tracks = get_tracks_in_playlist(token, id)
    print(tracks[0])
    songs = [track["track"] for track in tracks]
    all_song_names.append([song["name"] for song in songs])
    all_song_ids.append([song["id"] for song in songs])
    acoustics = get_audio_features_of_songs(token, songs)
    acoustics = [song for song in acoustics if song != None]
    tempos = [song["tempo"] for song in acoustics]
    if len(tempos) != 50:
        tempos.append(int(np.average(tempos)))
    all_tempos.append(tempos)
    av_tempos.append(np.average(tempos))

print(all_song_names[0])
print(all_song_ids[0])
quit()

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

