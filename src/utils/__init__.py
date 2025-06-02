import os
from pathlib import Path
import random
import shutil
import string
from .ffmpeg import authenticate_ffmpeg
from .ffmpeg import update_ffmpeg_path
from .ffmpeg import download_ffmpeg

def generate_transcript(data):
    return ' '.join(item['content'] for item in data if 'content' in item)

def clear_temp(temp_dir="temp"):
    temp_path = Path(temp_dir)
    if not temp_path.exists() or not temp_path.is_dir():
        return 
    for item in temp_path.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

def rename_file(file_path, suffix):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    base_dir, original_filename = os.path.split(file_path)
    _, ext = os.path.splitext(original_filename)
    random_string = ''.join(random.choices(string.ascii_letters, k=random.randint(8, 12)))
    new_filename = f"{random_string}_{suffix}{ext}"
    new_full_path = os.path.join(base_dir, new_filename)
    os.rename(file_path, new_full_path)
    return new_full_path