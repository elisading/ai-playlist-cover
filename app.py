from flask import Flask, redirect, request, jsonify, session, render_template
import requests
import secrets
import binascii
import urllib.parse
from datetime import datetime, timedelta
import os
import openai
from spotify import utils, openai_utils
from collections import Counter

app = Flask(__name__)

#random_bytes = secrets.token_bytes(32)
#secret_key_hex = binascii.hexlify(random_bytes).decode()
#print(secret_key_hex)

app.secret_key = os.getenv("APP_SECRET_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")
REDIRECT_URI="http://localhost:5000/callback"

AUTH_URL="https://accounts.spotify.com/authorize"
TOKEN_URL="https://accounts.spotify.com/api/token"
API_BASE_URL="https://api.spotify.com/v1"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
# user-top-read user-read-recently-played
def login():
    scope = "ugc-image-upload playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public"

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": REDIRECT_URI,
        # omit for final ver, for testing only
        "show_dialog": True
    }

    auth_url = f"{AUTH_URL}/?{urllib.parse.urlencode(params)}"

    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    if 'code' in request.args:
        request_body = {
            "grant_type": "authorization_code",
            "code": request.args['code'],
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }

    response = requests.post(TOKEN_URL, data=request_body)
    token_info = response.json()

    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

    return redirect('/playlists')

@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh_token')
    
    headers = {
        "Authorization": f"Bearer {session['access_token']}"
    }

    # get user id
    me_response = requests.get(f"{API_BASE_URL}/me", headers=headers)
    me_data = me_response.json()
    user_id = me_data['id']

    response = requests.get(f"{API_BASE_URL}/me/playlists", headers=headers)
    playlists_data = response.json()

    playlists = []
    for playlist_item in playlists_data.get('items', []):
        if playlist_item['owner']['id'] == user_id:
            playlist = {
                "name": playlist_item.get('name', "Unknown Name"),
                "description": playlist_item.get('description', "No Description"),
                "id": playlist_item.get('id', "Unknown ID"),
                "owner": {
                    "id": playlist_item['owner']['id'],
                    "display_name": playlist_item['owner'].get('display_name', "Unknown Owner")
                },
                "image_url": playlist_item['images'][0]['url'] if playlist_item.get('images') else None
            }
            playlists.append(playlist)

    return render_template('playlists.html', playlists=playlists)

@app.route('/refresh_token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        request_body = {
            "grant_type": "refresh_token",
            "refresh_token": session['refresh_token'],
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=request_body)
        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

        return redirect('/playlists')
    
@app.route('/playlists/<playlist_id>')
def playlist_detail(playlist_id):
    # Fetch playlist details
    playlist_data = utils.get_playlist_details(playlist_id, session['access_token'])
    playlist_name = playlist_data['name']
    playlist_image_url = playlist_data['images'][0]['url'] if playlist_data.get('images') else None

    # Fetch tracks
    track_data = utils.get_playlist_tracks(playlist_id, session['access_token'])
    tracks = track_data['items']

    return render_template('playlist_detail.html', tracks=tracks, playlist_name=playlist_name, playlist_image_url=playlist_image_url)

@app.route('/playlists/<playlist_id>/generate_image', methods=['POST'])
def generate_image(playlist_id):
    print("Generate Image Route Triggered for Playlist ID:", playlist_id);
    track_data = utils.get_playlist_tracks(playlist_id, session['access_token'])
    tracks = track_data['items']

    artist_ids = list({track['track']['artists'][0]['id'] for track in tracks})
    artist_names = []
    artist_genres = []

    for artist_id in artist_ids:
        artist_data = utils.get_artist_details(artist_id, session['access_token'])
        artist_names.append(artist_data['name'])
        artist_genres.extend(artist_data['genres'])

    popular_artists = [item[0] for item in Counter(artist_names).most_common(3)]
    popular_genres = [item[0] for item in Counter(artist_genres).most_common(3)]

    playlist_data = utils.get_playlist_details(playlist_id, session['access_token'])
    playlist_name = playlist_data['name']

    visual_description = openai_utils.generate_visual_prompt(popular_artists, popular_genres, playlist_name)
    
    image_response = openai.Image.create(
        prompt=visual_description,
        n=1,
        size="256x256",
    )

    image_url = image_response["data"][0]["url"]
    print("Generated Image URL:", image_url);

    return jsonify({"visual_description": visual_description, "image_url": image_url})

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)