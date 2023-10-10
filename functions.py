import requests


def get_playlist(playlist_id, access_token):

    url = f'https://api.spotify.com/v1/playlists/{playlist_id}'
    headers = get_auth_header(access_token)

    try:
        response = requests.get(endpoint_url, headers=headers)
        
        if response.status_code == 200:
            playlist_data = response.json()
            return playlist_data
        else:
            print(f'Error {response.status_code}')
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    
def get_user_playlists(user_id, access_token):
    url = f'https://api.spotify.com/v1/users/{user_id}/playlists'
    headers = get_auth_header(access_token)

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            playlists_data = response.json()['items']
            return playlists_data
        else:
            print(f"Failed to retrieve user's playlists. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def extract_songs_and_artists(playlist_data):
    song_titles = []
    artist_names = []

    for item in playlist_data['tracks']['items']:
        track = item['track']

        title = track['name']
        artist_names_list = [artist['name'] for artist in track['artists']]

        song_titles.append(title)
        artist_names.append(artist_names_list)

    return song_titles, artist_names

