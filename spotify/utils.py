import requests
import base64
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from PIL import Image
import io

urllib3.disable_warnings(InsecureRequestWarning)

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
    print(f"Fetching image from URL: {image_url}")
    response = requests.get(image_url)
    
    if response.status_code == 200:
        print("Image successfully fetched from URL.")
        compressed_image = compress_image(response.content)
        image_data = base64.b64encode(compressed_image).decode('utf-8')
        print("Image successfully converted to base64.")
        return image_data
    else:
        print(f"Failed to fetch image from URL. Status code: {response.status_code}")
        response.raise_for_status()

def upload_to_spotify(playlist_id, image_base64, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "image/jpeg"
    }
    response = requests.put(f"{API_BASE_URL}/playlists/{playlist_id}/images", headers=headers, data=image_base64.encode('utf-8'), verify=False)
    print(f"Response Code: {response.status_code}")
    print(f"Response Content: {response.text}")
    return response.json()

def compress_image(image_data, max_size_kb=256):
    with Image.open(io.BytesIO(image_data)) as img:
        img_format = img.format
        output = io.BytesIO()
        quality = 85
        img.save(output, format=img_format, quality=quality)
        
        while output.tell() / 1024 > max_size_kb and quality > 10:
            output = io.BytesIO()
            quality -= 5
            img.save(output, format=img_format, quality=quality)
        
        return output.getvalue()