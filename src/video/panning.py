import json 
import subprocess
import torch
from pathlib import Path

ffmpeg = json.load(open(Path("data/settings/ffmpeg.json")))["path"]

def generate(
    image_path,
    duration,
    video_name="panning_image.mp4",
    crf=28,
    settings=None
):
    output_path = str(Path("temp") / video_name)
    fps = settings.get("fps", 25)
    resolution = settings.get("resolution", "1080x1920")
    zoom_speed = settings.get("zoom_speed", 0.010)

    # Check for cuda if not use cpu
    use_gpu = torch.cuda.is_available() or settings.get("force_cuda", False)

    codec = "h264_nvenc" if use_gpu else "libx264"
    hwaccel = ["-hwaccel", "cuda"] if use_gpu else []

    res_w, res_h = map(int, resolution.split("x"))
    total_frames = int(duration * fps)

    zoom_filter = (
        f"scale=8000:-1,"
        f"zoompan="
          f"z='min(zoom+{zoom_speed},1.5)':"
          f"x='iw/2-(iw/zoom/2)':"
          f"y='ih/2-(ih/zoom/2)':"
          f"d={total_frames}:"
          f"s={res_w}x{res_h}:fps={fps},"
        "format=yuv420p"
    )

    cmd = [
        ffmpeg,
        "-y",
        *hwaccel,
        "-loop", "1", "-i", image_path,
        "-vf", zoom_filter,
        "-t", str(duration),
        "-c:v", codec,
        "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        output_path
    ]
    subprocess.run(cmd, check=True)

    return output_path