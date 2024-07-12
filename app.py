from flask import Flask, redirect, request, jsonify, session, render_template, send_file
import requests
import secrets
import binascii
import urllib.parse
from datetime import datetime, timedelta
import os
import openai
from spotify import utils, openai_utils
from collections import Counter
from io import BytesIO
import logging

app = Flask(__name__)


app.secret_key = os.getenv("APP_SECRET_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")

REDIRECT_URI = "https://audiart-git-debugging-elisadings-projects.vercel.app/callback"

AUTH_URL="https://accounts.spotify.com/authorize"
TOKEN_URL="https://accounts.spotify.com/api/token"
API_BASE_URL="https://api.spotify.com/v1"

logging.basicConfig(level=logging.DEBUG)

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
@app.route('/playlists/<int:page>')
def get_playlists(page=1):
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh_token')

    headers = {
        "Authorization": f"Bearer {session['access_token']}"
    }

    limit = 10
    offset = (page - 1) * limit

    me_response = requests.get(f"{API_BASE_URL}/me", headers=headers)
    me_data = me_response.json()
    user_id = me_data['id']

    response = requests.get(f"{API_BASE_URL}/me/playlists?limit={limit}&offset={offset}", headers=headers)
    playlists_data = response.json()

    playlists = []
    playlist_ids = set()
    for playlist_item in playlists_data.get('items', []):
        playlist_id = playlist_item.get('id', "Unknown ID")
        if playlist_item['owner']['id'] == user_id and playlist_id not in playlist_ids:
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
            playlist_ids.add(playlist_id)

    return render_template('playlists.html', playlists=playlists, page=page, total_pages=(playlists_data['total'] // limit) + 1)


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
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "No access token found"}), 401
    playlist_data = utils.get_playlist_details(playlist_id, session['access_token'])
    
    playlist_name = playlist_data.get('name', 'Unknown Name')
    playlist_image_url = playlist_data['images'][0]['url'] if playlist_data.get('images') else None

    track_data = utils.get_playlist_tracks(playlist_id, session['access_token'])
    tracks = track_data['items']

    return render_template('playlist_detail.html', tracks=tracks, playlist_name=playlist_name, playlist_image_url=playlist_image_url, playlist_id=playlist_id)


@app.route('/playlists/<playlist_id>/generate_image', methods=['POST'])
def generate_image_route(playlist_id):
    logging.debug(f"Generate Image Route Triggered for Playlist ID: {playlist_id}")
    try:
        track_data = utils.get_playlist_tracks(playlist_id, session['access_token'])
        tracks = track_data['items']

        artist_ids = list({track['track']['artists'][0]['id'] for track in tracks})

        artist_names = []
        artist_genres = []
        for artist_id in artist_ids:
            artist_data = utils.get_artist_details(artist_id, session['access_token'])
            artist_names.append(artist_data['name'])
            artist_genres.extend(artist_data['genres'])

        popular_artists = [item[0] for item in Counter(artist_names).most_common(5)]
        popular_genres = [item[0] for item in Counter(artist_genres).most_common(5)]
        logging.debug(f"Popular artists: {popular_artists}")
        logging.debug(f"Popular genres: {popular_genres}")

        # Get playlist details
        playlist_data = utils.get_playlist_details(playlist_id, session['access_token'])
        playlist_name = playlist_data['name']
        logging.debug(f"Playlist name: {playlist_name}")

        visual_description = openai_utils.generate_visual_prompt(popular_artists, popular_genres, playlist_name, tracks)
        logging.debug(f"Visual prompt generated: {visual_description}")

        logging.debug("Starting image generation")
        image_url = openai_utils.generate_image_from_prompt(visual_description)
        logging.debug(f"Image generated: {image_url}")

        return jsonify({"visual_description": visual_description, "image_url": image_url})
    except Exception as e:
        logging.error(f"Error in generate_image_route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/playlists/<playlist_id>/upload_image', methods=['POST'])
def upload_image_to_spotify(playlist_id):
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "No access token found"}), 401

    image_url = request.json.get('image_url')
    if not image_url:
        return jsonify({"error": "No image URL provided"}), 400

    try:
        image_base64 = utils.convert_image_to_base64(image_url)
        result = utils.upload_to_spotify(playlist_id, image_base64, access_token)
        return jsonify(result)
    except Exception as e:
        print(f"Error uploading image: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/download_image')
def download_image():
    image_url = request.args.get('url')
    if not image_url:
        return "No URL provided", 400

    response = requests.get(image_url)
    if response.status_code != 200:
        return "Image could not be retrieved", 404

    image = BytesIO(response.content)
    return send_file(image, mimetype='image/jpeg', as_attachment=True, attachment_filename='playlist_cover.jpg')

# if __name__ == '__main__':
#     app.run(debug=True)