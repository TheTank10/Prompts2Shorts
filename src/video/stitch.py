import subprocess
import random
from pathlib import Path
import json
import torch
import cv2
from mutagen.mp3 import MP3

TRANSITIONS = [
    "fade",
    "fadeblack",
    "fadewhite",
    "wipeleft",
    "wiperight",
    "wipeup",
    "wipedown",
    "slideleft",
    "slideright",
    "slideup",
    "slidedown",
    "circleopen",
    "circleclose",
    "circlecrop",
    "radial",
    "diagtl",
    "diagtr",
    "diagbl",
    "diagbr",
    "hlslice",
    "hrslice",
    "vuslice",
    "vdslice",
    "smoothleft",
    "smoothright",
    "smoothup",
    "smoothdown",
    "distance",
    "pixelize",
    "blurblack",
    "blurwhite",
]

ffmpeg = json.load(open(Path("data/settings/ffmpeg.json")))["path"]
project_root = Path(__file__).resolve().parents[2]

def escape_colons(path):
    return path.replace(":", "\\:")

def get_video_duration(video_path):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path!r}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()
    if fps <= 0 or frames <= 0:
        raise RuntimeError(f"Invalid metadata for {video_path!r} (fps={fps}, frames={frames})")
    return frames / fps

def generate(
    video_list,
    audio_path,
    ass_file=None,
    settings=None,
    video_name='final_video.mp4',
    print_mode=True,
    crf=28,
    audio_bitrate='96k',
):
    video_paths = [Path(v) for v in video_list]
    durations = [get_video_duration(vp) for vp in video_paths]

    transition_duration = settings.get("transition_duration", 0.3)
    audio_duration = MP3(audio_path).info.length

    offsets = []
    total = 0.0
    for i, d in enumerate(durations[:-1]):
        total += d
        offsets.append(total - (i + 1) * transition_duration)

    use_gpu = torch.cuda.is_available() or (settings and settings.get("force_cuda", False))
    codec = "h264_nvenc" if use_gpu else "libx264"
    hwaccel = ["-hwaccel", "cuda"] if use_gpu else []

    inputs = []
    for vp in video_paths:
        inputs.extend(["-i", str(vp)])
    inputs.extend(["-i", str(audio_path)])

    transition_type = settings.get("transition", "random")
    transition_type = transition_type.split(",") if "," in transition_type else [transition_type]
    transition_index = 0

    filter_parts = []
    for idx in range(len(video_paths)):
        filter_parts.append(f"[{idx}:v]format=yuv420p[v{idx}];")
    for i in range(len(video_paths) - 1):

        transition = transition_type[transition_index % len(transition_type)].lower().strip()
        transition_index += 1

        if transition == "random":
            transition = random.choice(TRANSITIONS)

        left = "v0" if i == 0 else f"vf{i}"
        right = f"v{i+1}"
        out_tag = f"vf{i+1}"
        off = offsets[i]
        filter_parts.append(
            f"[{left}][{right}]xfade={transition}:"
            f"duration={transition_duration}:offset={off}[{out_tag}];"
        )
    last_tag = f"vf{len(video_paths) - 1}"
    filter_parts.append(f"[{last_tag}]format=yuv420p[outv]")
    filter_complex = "".join(filter_parts)

    if ass_file:
        esc = escape_colons(str(Path(ass_file).as_posix()))
        fonts = "data/fonts"
        filter_complex += f";[outv]ass={esc}:fontsdir={fonts}[outvv]"
        video_tag = "[outvv]"
    else:
        video_tag = "[outv]"

    audio_index = len(video_paths)
    cmd = [
        ffmpeg, "-y", *hwaccel, *inputs,
        "-filter_complex", filter_complex,
        "-map", video_tag,
        "-map", f"{audio_index}:a",
        "-c:v", codec, "-preset", "veryfast", "-crf", str(crf),
        "-c:a", "aac", "-b:a", audio_bitrate,
        "-movflags", "+faststart", "-t", f"{audio_duration}",
        str(Path("output") / video_name)
    ]

    if print_mode:
        subprocess.run(cmd, check=True, cwd=str(project_root))
    else:
        subprocess.run(
            cmd,
            check=True,
            cwd=str(project_root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    return str(Path("output") / video_name)