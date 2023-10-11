import openai

# and artists such as {', '.join(artists)}
# describe details and composition

def generate_visual_prompt(artists, genres, playlist_name):
    message = [{
        "role": "system",
        #"content": "You’re an expert in image prompt generation. Creatively describe an artwork with a specific art style, mention colors and emotions, avoid text in the image."
        "content": "You are tasked with creating a detailed and evocative description for an artwork to be used as a playlist cover. The art should resonate with the mood, genre, and themes of the music (avoid people and text in the image)."
    }, {
        "role": "user",
        "content": f"I have a playlist named {playlist_name} with genres of {', '.join(genres)}. Pick a suitable art style and describe a painting matching the playlist mood in one sentence."
    }]
    print(genres)
    print(artists)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        #max_tokens=100,
        temperature=0.4,
        messages=message
    )

    return response['choices'][0]['message']['content']
