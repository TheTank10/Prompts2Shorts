import subprocess
import json
import os
from pathlib import Path

ffmpeg = json.load(open(Path("data/settings/ffmpeg.json")))["path"]

def concatenate_audio(audio_paths, audio_name="concatenated_audio.mp3"):
    if not audio_paths:
        raise ValueError("No audio files to concatenate.")

    output = str(Path("temp") / audio_name)

    with open("concat_list.txt", "w") as f:
        for path in audio_paths:
            f.write(f"file '{path}'\n")

    cmd = [
        ffmpeg,
        "-f", "concat",
        "-safe", "0",
        "-i", "concat_list.txt",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        output
    ]

    # Avoids the ffmpeg y/N
    if os.path.exists(output):
        os.remove(output)

    subprocess.run(cmd, check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    os.remove("concat_list.txt")

    for path in audio_paths:
        os.remove(path)

    return output