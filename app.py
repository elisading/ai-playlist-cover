from flask import Flask, redirect, request, jsonify, session
import requests
import secrets
import binascii
import urllib.parse
from datetime import datetime, timedelta

app = Flask(__name__)

#random_bytes = secrets.token_bytes(32)
#secret_key_hex = binascii.hexlify(random_bytes).decode()
#print(secret_key_hex)

app.secret_key = '7685fd6af40d593040a056863e48ba1a07a204bc41ea49f6862790cd619dc2cf'

CLIENT_ID="54982161898f4302b087cff0eb51237b"
CLIENT_SECRET="8ec5de7516e1431580da5e3cfe426b5f"
REDIRECT_URI="http://localhost:5000/callback"

AUTH_URL="https://accounts.spotify.com/authorize"
TOKEN_URL="https://accounts.spotify.com/api/token"
API_BASE_URL="https://api.spotify.com/v1"


@app.route('/')
def index():
    return "Create the best art for your playlists, ever! <a href='/login'>Login with Spotify</a>"

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

    response = requests.get(f"{API_BASE_URL}/me/playlists", headers=headers)
    playlists_data = response.json()

    playlists = []
    for playlist_item in playlists_data.get('items', []):
        playlist = {
            "name": playlist_item.get('name', "Unknown Name"),
            "description": playlist_item.get('description', "No Description"),
            "owner": {
                "id": playlist_item['owner']['id'],
                "display_name": playlist_item['owner'].get('display_name', "Unknown Owner")
            },
            "image_url": playlist_item['images'][0]['url'] if playlist_item.get('images') else None
        }
        playlists.append(playlist)

    return jsonify(playlists)

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
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)