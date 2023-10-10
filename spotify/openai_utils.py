import openai

# and artists such as {', '.join(artists)}

def generate_visual_prompt(artists, genres, playlist_name):
    message = [{
        "role": "system",
        "content": "You’re an expert in image prompt generation. Describe an image with a specific art style, describe details and composition, mention colors and emotions."
    }, {
        "role": "user",
        "content": f"I have a playlist named {playlist_name} with genres of {', '.join(genres)}. Describe an image with this mood in 2-3 sentences, be highly detailed yet succinct."
    }]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        #max_tokens=100,
        #temperature=1.2,
        messages=message
    )

    return response['choices'][0]['message']['content']
