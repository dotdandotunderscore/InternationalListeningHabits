import numpy as np
import pandas as pd
import plotly.express as px
# import plotly.figure_factory as ff
import plotly.graph_objects as go
import datetime, time
from spotipy import *

current_date = datetime.date.today()
token = get_token()

if (os.path.isfile(os.getcwd()+'//code//all_names.npy') and os.path.isfile(os.getcwd()+'//code//all_ids.npy') 
    and os.path.isfile(os.getcwd()+'//code//all_song_names.npy') and os.path.isfile(os.getcwd()+'//code//all_song_ids.npy')
    and os.path.isfile(os.getcwd()+'//code//all_afs.npy') and time.time() - os.path.getmtime(os.getcwd()+'//code//all_names.npy') < 18000):
    all_names = np.load(os.getcwd()+'//code//all_names.npy', allow_pickle=True)[1:]
    all_ids = np.load(os.getcwd()+'//code//all_ids.npy', allow_pickle=True)[1:]
    all_song_names = np.load(os.getcwd()+'//code//all_song_names.npy', allow_pickle=True)
    all_song_ids = np.load(os.getcwd()+'//code//all_song_ids.npy', allow_pickle=True)
else:
    all_names, all_ids = get_spotify_top_50s(token)
    np.save(os.getcwd()+'//code//all_names.npy', all_names)
    np.save(os.getcwd()+'//code//all_ids.npy', all_ids)
    all_names = all_names[1:]
    all_ids = all_ids[1:]

    all_song_names, all_song_ids = get_songs_from_playlists(token, all_ids)
    all_afs = get_audio_features_of_song_ids_from_playlists(token, all_song_ids)
    np.save(os.getcwd()+'//code//all_song_names.npy', all_song_names)
    np.save(os.getcwd()+'//code//all_song_ids.npy', all_song_ids)
    np.save(os.getcwd()+'//code//all_afs.npy', all_afs)

countries = [country[9:] for country in all_names]
countries, all_song_names = zip(*sorted(zip(countries, all_song_names)))
num_countries = len(countries)
all_shared_num = []
for i in range(num_countries):
    num_shared = []
    for j in range(num_countries):
        if i == j:
            num_shared.append(50)
        else:
            shares = len([song for song in all_song_names[i] if song in all_song_names[j]])
            num_shared.append(shares)
    all_shared_num.append(num_shared)

datas_text = [[str(y) for y in x] for x in all_shared_num]

# fig = ff.create_annotated_heatmap(all_shared_num, x=countries, y=countries, annotation_text=datas_text, colorscale='Viridis')
fig = go.Figure(data=go.Heatmap(z=all_shared_num, x=countries, y=countries, type='heatmap', colorscale='Viridis'))
fig['layout']['yaxis']['autorange'] = "reversed"
fig.update_layout(title_text="Songs shared between Top 50 playlists")
fig['data'][0]['showscale'] = True
fig.write_html(os.getcwd()+f'//code//SharedSongs//SharedHeatmap.html')
fig.show()

av_prep = [[x for x in y if x!=50] for y in all_shared_num]
average_shared = [round(sum(x)/len(x), 2) for x in av_prep]
average_shared, countries = zip(*sorted(zip(average_shared, countries)))

average_df = pd.DataFrame({
    "Country":countries,
    "Average shared songs":average_shared
})
fig = px.histogram(average_df, x='Country', y="Average shared songs")
fig['layout']['xaxis']['autorange'] = "reversed"
fig.update_layout(title_text='Average shared songs between Top 50 playlists',yaxis_title_text='Average shared songs')
fig.write_html(os.getcwd()+f'//code//SharedSongs//SharedHist.html')
fig.show()