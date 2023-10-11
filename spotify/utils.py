import requests
import base64

API_BASE_URL="https://api.spotify.com/v1"

def get_playlist_tracks(playlist_id, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"{API_BASE_URL}/playlists/{playlist_id}/tracks", headers=headers)
    return response.json()

def get_playlist_details(playlist_id, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"{API_BASE_URL}/playlists/{playlist_id}", headers=headers)
    return response.json()

def get_artist_details(artist_id, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"{API_BASE_URL}/artists/{artist_id}", headers=headers)
    return response.json()

def convert_image_to_base64(image_url):
    response = requests.get(image_url)
    image_data = base64.b64encode(response.content).decode('utf-8')
    return image_data

def upload_to_spotify(playlist_id, image_base64, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "image/jpeg"
    }
    response = requests.put(f"{API_BASE_URL}/playlists/{playlist_id}/images", headers=headers, data=image_base64.encode('utf-8'))
    return response.json()