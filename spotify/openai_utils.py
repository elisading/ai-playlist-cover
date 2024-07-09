import openai
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()


def generate_visual_prompt(artists, genres, playlist_name, tracks):
    track_artist_names = [f"{track['track']['name']} by {track['track']['artists'][0]['name']}" for track in tracks]
    if len(track_artist_names) > 20:
        track_artist_names = track_artist_names[:20]
    print("truncated tracks: ", track_artist_names)
    message = [{
        "role": "system",
        "content": "You are an abstract artist tasked with creating a visual concept for playlist cover art. Describe an abstract, mood-evoking scene that captures the essence of the playlist without referencing specific objects, people, or text. Focus on colors, textures, patterns, and overall atmosphere. Keep your description concise, under 100 words, and avoid mentioning any song titles or artist names."

    }, {
        "role": "user",
         "content": f"Create an abstract visual concept for a playlist named '{playlist_name}'. The playlist's mood is derived from these tracks: {', '.join(track_artist_names)}. Describe a scene that evokes the playlist's atmosphere without mentioning specific objects or using words in the image."

    }]
    print("Genres: ", genres)
    print("Artists: ", artists)

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        messages=message
    )

    content = response.choices[0].message.content

    print("Visual prompt: ", content)
    print("Prompt length: ", len(content))
    return content

def generate_image_from_prompt(prompt):
    image_response = client.images.generate(
        model="dall-e-2",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = image_response.data[0].url
    print("Generated Image URL:", image_url)

    return image_url

