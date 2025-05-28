# Audio is generated using the pollinations API: https://github.com/pollinations/pollinations

import requests
from urllib.parse import quote_plus
from mutagen.mp3 import MP3
from pathlib import Path

def generate(text, voice, style, audio_name="tts_audio.mp3"):
    prompt = f'Read ALL of this. From the first quotation mark to the last: "{text}"\nVoice Style: {style}.'
    encoded = quote_plus(prompt)
    url = f"https://text.pollinations.ai/{encoded}?model=openai-audio&voice={quote_plus(voice)}"
    
    resp = requests.get(url)
    resp.raise_for_status()
    
    audio_path = str(Path("temp") / audio_name)

    with open(audio_path, "wb") as f:
        f.write(resp.content)

    audio = MP3(audio_path)
    duration = audio.info.length

    return audio_path, duration