from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_visual_prompt(artists, genres, playlist_name, tracks, style="abstract"):
    track_artist_names = [f"{track['track']['name']} by {track['track']['artists'][0]['name']}" for track in tracks]
    if len(track_artist_names) > 20:
        track_artist_names = track_artist_names[:20]
    print("truncated tracks: ", track_artist_names)
    
    # Define system prompts based on style
    system_prompts = {
        "abstract": "You are an abstract visual artist creating a playlist cover concept. Describe a mood-evoking, non-representational scene that captures the playlist's essence. Focus on colors, textures, shapes, movement, and atmosphere. Avoid referencing song titles, artist names, or specific recognizable objects and people. Do not include text in the image. Use vivid, sensory language to convey feeling while remaining concise, under 100 words.",
        "photorealistic": "You are a world-class visual artist creating photorealistic playlist cover art. Describe a highly detailed, realistic scene that captures the playlist's vibe. You may include objects, settings, and characters, but avoid text or explicit logos. Focus on vivid sensory details: lighting, textures, colors, environment, and atmosphere. Compose the scene as a compelling photograph or cinematic still. Keep under 100 words.",
        "ghibli": "You are a Studio Ghibli-style illustrator creating playlist cover art. Describe a scene inspired by Ghibli aesthetics: soft painterly textures, vibrant yet natural colors, atmospheric lighting, and whimsical details. Include gentle, expressive characters, nature elements, or magical realism themes typical of illustrated films. Avoid text or logos. Focus on mood, subtle storytelling, and visual harmony. Keep under 100 words."
    }
    
    message = [{
        "role": "system",
        "content": system_prompts.get(style, system_prompts["abstract"])
    }, {
        "role": "user",
         "content": f"Create a {style} visual concept for a playlist named '{playlist_name}'. The playlist's mood is derived from these tracks: {', '.join(track_artist_names)}. Describe a scene that evokes the playlist's atmosphere."
    }]
    print("Genres: ", genres)
    print("Artists: ", artists)

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        temperature=1,
        messages=message
    )

    content = response.choices[0].message.content

    print("Visual prompt: ", content)
    print("Prompt length: ", len(content))
    return content

def generate_image_from_prompt(prompt):
    image_response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        quality="auto",
        n=1,
    )

    image_base64 = image_response.data[0].b64_json
    print("Generated Image base64 length:", len(image_base64))

    return image_base64