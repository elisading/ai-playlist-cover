from dotenv import load_dotenv
import os
import base64
import requests
from requests import post, get
import json

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_string_bytes = auth_string.encode('utf-8')
    auth_base64_bytes = base64.b64encode(auth_string_bytes)

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64_bytes.decode('utf-8'),
        "Content-Type": "application/x-www-form-urlencoded"
        }
    data = {"grant_type": "client_credentials"}

    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]

    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def get_playlist(playlist_id, access_token):
    """
    Get a playlist from a user's Spotify account using the Web API.

    Args:
        playlist_id (str): The unique identifier of the playlist.
        access_token (str): The user's Spotify access token.

    Returns:
        dict: The JSON response containing playlist information.
    """

    url = f'https://api.spotify.com/v1/playlists/{playlist_id}'
    headers = get_auth_header(access_token)

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            playlist_data = response.json()
            return playlist_data
        else:
            print(f'Error {response.status_code}')
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

token = get_token()
print(token)