import requests

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
