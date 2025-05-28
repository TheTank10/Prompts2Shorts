import json
import os
from pathlib import Path
import random
import shutil
import string
import subprocess
import sys

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

def authenticate_ffmpeg():
    settings = str(Path("data/settings/ffmpeg.json"))
    
    try:
        p = json.load(open(settings))["path"]
    except:
        p = None
    while True:
        if p:
            try:
                out = subprocess.run([p, "-version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True, text=True).stdout
                if "ffmpeg version" in out.lower():
                    break
            except:
                print("Error: Invalid ffmpeg path.\n* Make sure you have entered a valid path to ffmpeg such as: C:\\ffmpeg\\ffmpeg-master-latest-win64-gpl-shared\\bin\\ffmpeg.exe\n* If you added ffmpeg to PATH you can enter 'ffmpeg' (recommended)")
        p = input("Path to ffmpeg: ").strip()
        if p.lower() in ("exit", "quit"):
            sys.exit(1)

    with open(settings, "w") as f:
        json.dump({"path": p}, f, indent=4)