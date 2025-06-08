import subprocess
import json
from pathlib import Path

ffmpeg_settings_path = Path("data/settings/ffmpeg.json")
ffmpeg_settings = json.load(open(ffmpeg_settings_path))
ffmpeg = ffmpeg_settings["path"]

def check_encoder(encoder_name):
    """Check if a specific encoder works using FFmpeg"""
    try:
        result = subprocess.run(
            [
                ffmpeg, "-f", "lavfi", "-i", "color=black:s=64x64:d=1",
                "-c:v", encoder_name, "-f", "null", "-"
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            timeout=5,
            text=True
        )
        error_output = result.stderr.lower()
        # Detect common failure messages
        if any(term in error_output for term in [
            "error", "cannot", "failed", "invalid", "not found", "unsupported"
        ]):
            return False
        return True
    except Exception:
        return False

def get_codec():
    if ffmpeg_settings.get("codec", None):
        return ffmpeg_settings["codec"]

    # Ordered by preference: fastest to slowest
    preferred_encoders = [
        "h264_nvenc",    # NVIDIA GPU
        "hevc_nvenc",    # NVIDIA GPU
        "h264_qsv",      # Intel QuickSync
        "hevc_qsv",      # Intel QuickSync
        "h264_amf",      # AMD GPU
        "hevc_amf",      # AMD GPU
        "libx264",       # CPU (universal)
        "libx265"        # CPU (slower, high quality)
    ]

    for encoder in preferred_encoders:
        if check_encoder(encoder):
            ffmpeg_settings["codec"] = encoder 
            json.dump(ffmpeg_settings, open(ffmpeg_settings_path, 'w'), indent=4)
            return encoder

    raise "No usable encoder found. Is FFmpeg installed correctly?"