import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from geopy import distance
from geopy.geocoders import Nominatim
import datetime, time, pickle
from spotipy import *

current_date = datetime.date.today()
token = get_token()
geolocator = Nominatim(user_agent="MyApp")

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
num_countries = len(countries)
all_shared = []
all_shared_num = []
for i in range(num_countries):
    country_shared = []
    num_shared = []
    for j in range(num_countries):
        if i == j:
            country_shared.append([None])
            num_shared.append([None])
        else:
            matches = [song for song in all_song_names[i] if song in all_song_names[j]]
            shares = len(matches)
            country_shared.append(matches)
            num_shared.append(shares)
    all_shared.append(country_shared)
    all_shared_num.append(num_shared)

if os.path.isfile(os.getcwd()+'//code//country_locs.pkl'):
    with open(os.getcwd()+'//code//country_locs.pkl', 'rb') as fp:
        country_locs = pickle.load(fp)
else:
    country_locs = {}
    for country in countries:
        if country == 'Hong Kong':
            country_locs[country] = (geolocator.geocode({"city":country}).latitude, geolocator.geocode({"city":country}).longitude)
        else:
            country_locs[country] = (geolocator.geocode({"country":country}).latitude, geolocator.geocode({"country":country}).longitude)
    with open(os.getcwd()+"//code//country_locs.pkl", 'wb') as fp:
        pickle.dump(country_locs, fp)

for i in range(num_countries):
    current_countries = countries[:i]+countries[i+1:]
    current_shareds = all_shared_num[i][:i]+all_shared_num[i][i+1:]
    current_loc = geolocator.geocode(countries[i])
    
    current_distances = [int(distance.distance(country_locs[countries[i]], country_locs[country]).km) for country in current_countries]

    # sorted_shareds, sorted_countries, sorted_distances = zip(*(sorted(zip(current_shareds, current_countries, current_distances))))
    sorted_distances, sorted_shareds, sorted_countries = zip(*(sorted(zip(current_distances, current_shareds, current_countries))))

    country_df = pd.DataFrame({
        "Country": sorted_countries,
        "Shared Songs": sorted_shareds,
        "Distance in km": sorted_distances
    })

    fig = px.line(country_df, x="Country", y="Shared Songs",
                     title=f"'Top 50 - {countries[i]}' Spotify Playlist vs The World - Updated {current_date}",
                     markers=True, hover_data=['Country','Shared Songs', "Distance in km"])
    # fig2 = px.line(country_df, x="Country", y="Distance")
    # fig.add_trace(fig2.data[0])
    # fig['layout']['xaxis']['autorange'] = "reversed"
    # fig.show()
    # if i == 1:
    #     print(countries[i], current_countries)
    #     print(distance.distance(country_locs["Taiwan"], country_locs["Singapore"]).km/1000)
    # quit()
    fig.write_html(os.getcwd()+f'//code//SharedSongs//{countries[i]}.html')
