# Audio is generated using the pollinations API: https://github.com/pollinations/pollinations

import requests
import base64
from mutagen.mp3 import MP3
from pathlib import Path

voice_style = """
Affect: A gentle, curious narrator with a British accent, guiding a magical, child-friendly adventure through a fairy tale world.

Tone: Magical, warm, and inviting, creating a sense of wonder and excitement for young listeners.

Pacing: Steady and measured, with slight pauses to emphasize magical moments and maintain the storytelling flow.

Emotion: Wonder, curiosity, and a sense of adventure, with a lighthearted and positive vibe throughout.

Pronunciation: Clear and precise, with an emphasis on storytelling, ensuring the words are easy to follow and enchanting to listen to.

***Read ONLY the script between the triple quotes.***
"""

def generate(text, voice, audio_name="tts_audio.mp3"):
    prompt = f'Read ONLY the script between the triple quotes, and do NOT add anything else: """{text}"""\n\nFollow these instructions:\n\n{voice_style}'
    payload = {
        "model": "openai-audio",
        "modalities": ["text", "audio"],
        "audio": {"voice": voice, "format": "mp3"},
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "private": True
    }
    response = requests.post("https://text.pollinations.ai/openai", json=payload)
    response.raise_for_status()
    response_data = response.json()

    audio_data_base64 = response_data['choices'][0]['message']['audio']['data']
    audio_binary = base64.b64decode(audio_data_base64)
    file_path = Path("temp")/audio_name
    file_path_str = str(file_path)

    with open(file_path, 'wb') as f:
        f.write(audio_binary)

    return file_path_str, MP3(file_path_str).info.length