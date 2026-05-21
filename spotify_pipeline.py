import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime
import os
import requests
import sys

# ==========================================
# 1. Configuration (Using Secure Environment Variables)
# ==========================================
# GitHub Actions will inject these securely!
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:9090')

# ==========================================
# 2. Authentication
# ==========================================
def authenticate_spotify():
    print("Initiating Spotify authentication...")
    scope = "user-read-recently-played"
    auth_manager = SpotifyOAuth(client_id=CLIENT_ID,
                                client_secret=CLIENT_SECRET,
                                redirect_uri=REDIRECT_URI,
                                scope=scope,
                                open_browser=False) 
    sp = spotipy.Spotify(auth_manager=auth_manager)
    sp.current_user() 
    return sp

# ==========================================
# 3. Secondary API: Fetch Genres via iTunes
# ==========================================
def get_song_genre(track_name, artist_name):
    try:
        url = "https://itunes.apple.com/search"
        params = {'term': f"{track_name} {artist_name}", 'entity': 'song', 'limit': 1}
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['resultCount'] > 0:
                return data['results'][0].get('primaryGenreName', 'Unknown')
    except Exception as e:
        pass
    return 'Unknown'

# ==========================================
# 4. ETL Pipeline
# ==========================================
def run_pipeline():
    sp = authenticate_spotify()
    print("Extracting last 50 tracks from Spotify...")
    
    results = sp.current_user_recently_played(limit=50)
    if not results or not results['items']:
        print("No tracks found.")
        return

    print("Enriching data with Apple iTunes Genres...")
    tracks_data = []
    song_genre_cache = {} 
    
    for item in results['items']:
        track = item.get('track', {})
        if track.get('is_local') or not track.get('id'):
            continue

        track_name = track.get('name', 'Unknown')
        artist_name = track.get('artists', [{'name': 'Unknown'}])[0].get('name')
        cache_key = f"{track_name}_{artist_name}"
        
        if cache_key not in song_genre_cache:
            song_genre_cache[cache_key] = get_song_genre(track_name, artist_name)
            
        tracks_data.append({
            'track_name': track_name,
            'artist_name': artist_name,
            'album_name': track.get('album', {}).get('name', 'Unknown'),
            'album_type': track.get('album', {}).get('album_type', 'Unknown'),
            'release_year': track.get('album', {}).get('release_date', '1900')[:4],
            'explicit': track.get('explicit', False),
            'played_at': item.get('played_at'),
            'duration_mins': round(track.get('duration_ms', 0) / 60000, 2),
            'song_genre': song_genre_cache[cache_key]
        })

    df_new = pd.DataFrame(tracks_data)
    df_new['played_at'] = pd.to_datetime(df_new['played_at'], format='ISO8601').dt.tz_localize(None)

    # ==========================================
    # 5. Load & Deduplicate (Master DB)
    # ==========================================
    master_file = 'master_spotify_data.csv'
    
    if os.path.exists(master_file):
        print("Found existing Master DB. Appending new records...")
        df_historical = pd.read_csv(master_file)
        df_historical['played_at'] = pd.to_datetime(df_historical['played_at'], format='ISO8601')
        df_combined = pd.concat([df_historical, df_new])
        df_combined.drop_duplicates(subset=['played_at'], keep='first', inplace=True)
        df_combined.sort_values(by='played_at', ascending=False, inplace=True)
        df_combined.to_csv(master_file, index=False)
        print(f"[SUCCESS] Appended tracks. Master DB has {len(df_combined)} rows.")
    else:
        print("No Master DB found. Creating a new one...")
        df_new.to_csv(master_file, index=False)
        print(f"[SUCCESS] Created Master DB with {len(df_new)} rows.")

if __name__ == '__main__':
    run_pipeline()
