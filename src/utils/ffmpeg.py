import subprocess
import json
import sys
from pathlib import Path
import os
import platform
import subprocess
from urllib.request import urlretrieve
import tarfile
import zipfile

def update_ffmpeg_path(path):
    settings_path = str(Path("data/settings/ffmpeg.json"))
    settings = json.load(open(settings_path))
    settings["path"] = path
    json.dump(settings_path, settings, indent=4)

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
                print("Error: Invalid ffmpeg path.\n* Make sure you have entered a valid path to ffmpeg such as: C:\\ffmpeg\\ffmpeg-master-latest-win64-gpl-shared\\bin\\ffmpeg.exe\n* If you added ffmpeg to PATH you can enter 'ffmpeg' (recommended)\n* If you don't have FFmpeg downloaded you can exit this and run --downloadffmpeg to download it.\nIf this didn't work you can manually download FFmpeg and run --create to get this prompt.")
        p = input("Path to ffmpeg: ").strip()
        if p.lower() in ("exit", "quit"):
            sys.exit(1)

    with open(settings, "w") as f:
        json.dump({"path": p}, f, indent=4)

# Attempts to download FFmpeg from github
# Currentely tested on: Windows
def download_ffmpeg(download_dir="data/ffmpeg"):
    urls = {
        "Windows": "https://github.com/TheTank10/Prompts2Shorts/releases/download/ffmpeg-builds/win-64-ffmpeg-7.1.1-full_build.zip",
        "Darwin": "https://github.com/TheTank10/Prompts2Shorts/releases/download/ffmpeg-builds/mac-64-ffmpeg-7.1.1.zip",
        "Linux": "https://github.com/TheTank10/Prompts2Shorts/releases/download/ffmpeg-builds/linux-64-ffmpeg-master-latest-linux64-gpl.tar.xz"
    }

    system = platform.system()
    if system not in urls:
        raise RuntimeError(f"Unsupported OS: {system}\nCurrent supported OS: Windows, Macos, Linux.")

    url = urls[system]
    download_dir = Path(download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)

    filename = download_dir / os.path.basename(url)

    if not filename.exists():
        print(f"Downloading FFmpeg for {system}... \n* (This might take some time depending on your internet.)")
        urlretrieve(url, filename)
        print("Download complete.")
    else:
        print(f"FFmpeg already downloaded at {filename}")

    extract_path = download_dir / system.lower()
    if not extract_path.exists():
        print("* Extracting FFmpeg...")
        extract_path.mkdir(parents=True, exist_ok=True)

        if filename.suffixes[-2:] == ['.tar', '.xz']:
            with tarfile.open(filename, "r:xz") as tar:
                tar.extractall(path=extract_path)
        elif filename.suffix == '.zip':
            with zipfile.ZipFile(filename, "r") as zip_ref:
                zip_ref.extractall(extract_path)
        else:
            raise RuntimeError("Unknown archive format")
        print("* Extraction complete.")
        filename.unlink()
    else:
        print(f"FFmpeg already extracted at {extract_path}")

    ffmpeg_exec = "ffmpeg.exe" if system == "Windows" else "ffmpeg"

    for root, _, files in os.walk(extract_path):
        if ffmpeg_exec in files:
            ffmpeg_path = Path(root) / ffmpeg_exec
            print(f"* Found FFmpeg binary at: {ffmpeg_path}")
            return ffmpeg_path.resolve()

    print(f"FFmpeg executable not found after extraction.. \nRetry or manually download at: {urls[system]}.\nOnce downloaded extract it and provide the path to the ffmpeg.exe in data/settings/ffmpeg.json")
    raise RuntimeError("FFmpeg executable not found after extraction")