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
        # "content": "You are tasked with returning a prompt used directly in image generation for playlist cover art. The description should be detailed, creative, and evocative without cluttering the scene. The image should be cohesive and resonate with the mood, genre, and themes of the music (make sure there are no people or text). Do not reference specific songs or artists, aim for a natural, creative, and aesthetically pleasing look that aligns with a Pinterest-like aesthetic. Don't overcomplicate the scene or prompt."
        "content": "You are an abstract artist tasked with creating a visual concept for playlist cover art. Describe an abstract, mood-evoking scene that captures the essence of the playlist without referencing specific objects, people, or text. Focus on colors, textures, patterns, and overall atmosphere. Keep your description concise, under 100 words, and avoid mentioning any song titles or artist names."

    }, {
        "role": "user",
        # "content": f"I have a playlist named {playlist_name}. Pick a suitable style and describe in detail an image matching the playlist mood in less than 1000 characters. The tracks of {playlist_name} are: {', '.join(track_artist_names)}."
         "content": f"Create an abstract visual concept for a playlist named '{playlist_name}'. The playlist's mood is derived from these tracks: {', '.join(track_artist_names)}. Describe a scene that evokes the playlist's atmosphere without mentioning specific objects or using words in the image."

    }]
    # with genres of {', '.join(genres)}
    print("Genres: ", genres)
    print("Artists: ", artists)

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        messages=message
    )

    content = response.choices[0].message.content

    # print(response['choices'][0]['message']['content'])
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



#"content": "You’re an expert in image prompt generation. Creatively describe an artwork with a specific art style, mention colors and emotions, avoid text in the image."
    # response = openai.ChatCompletion.create(
    #     model="gpt-4o",
    #     temperature=0.4,
    #     messages=message
    # )