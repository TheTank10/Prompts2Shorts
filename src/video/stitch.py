import subprocess
import random
from pathlib import Path
import json
import torch
import cv2
from mutagen.mp3 import MP3

TRANSITIONS = [
    "fade", "fadeblack", "fadewhite", "wipeleft", "wiperight", "wipeup",
    "wipedown", "slideleft", "slideright", "slideup", "slidedown",
    "circleopen", "circleclose", "circlecrop", "radial", "diagtl",
    "diagtr", "diagbl", "diagbr", "hlslice", "hrslice", "vuslice",
    "vdslice", "smoothleft", "smoothright", "smoothup", "smoothdown",
    "distance", "pixelize",
]

missing_transitions = ["blurblack", "blurwhite"] # Idk where the fuck they are

ffmpeg = json.load(open(Path("data/settings/ffmpeg.json")))["path"]
project_root = Path(__file__).resolve().parents[2]

def escape_colons(path: str) -> str:
    return path.replace(":", "\\:")

def get_video_duration(video_path: Path) -> float:
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
    video_name="final_video.mp4",
    print_mode=True,
    crf=28,
    audio_bitrate="96k",
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

    need_transition_sfx = len(video_paths) > 1 and len(offsets) > 0
    if need_transition_sfx:
        transition_sfx_path = project_root / "data" / "sound" / "transition.mp3"
        inputs.extend(["-i", str(transition_sfx_path)])

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
            f"[{left}][{right}]xfade={transition}:duration={transition_duration}:offset={off}[{out_tag}];"
        )

    last_tag = f"vf{len(video_paths) - 1}"
    filter_parts.append(f"[{last_tag}]format=yuv420p[outv]")

    if ass_file:
        esc_ass = escape_colons(str(Path(ass_file).as_posix()))
        fonts_dir = "data/fonts"
        filter_parts.append(f";[outv]ass={esc_ass}:fontsdir={fonts_dir}[outvv]")
        video_tag = "[outvv]"
    else:
        video_tag = "[outv]"

    audio_index = len(video_paths)
    if need_transition_sfx:
        trans_index = len(video_paths) + 1
        num_transitions = len(offsets)

        split_labels = [f"ts{i}" for i in range(num_transitions)]
        delay_labels = [f"del{i}" for i in range(num_transitions)]

        asplit_part = f"[{trans_index}:a]asplit={num_transitions}" + "".join(f"[{l}]" for l in split_labels)
        filter_parts.append(f";{asplit_part};")

        for i, off in enumerate(offsets):
            ms = int(off * 1000)
            filter_parts.append(f"[{split_labels[i]}]adelay={ms}:all=1[{delay_labels[i]}];")

        filter_parts.append(f"[{audio_index}:a]asetpts=PTS-STARTPTS[main];")

        all_mix_inputs = "[main]" + "".join(f"[{lbl}]" for lbl in delay_labels)
        amix_part = f"{all_mix_inputs}amix=inputs={num_transitions + 1}:normalize=0[mixa]"
        filter_parts.append(amix_part)

        audio_tag = "[mixa]"
    else:
        audio_tag = f"{audio_index}:a"

    filter_complex = "".join(filter_parts)

    cmd = [
        ffmpeg,
        "-y",
        *hwaccel,
        *inputs,
        "-filter_complex", filter_complex,
        "-map", video_tag,
        "-map", audio_tag,
        "-c:v", codec,
        "-preset", "veryfast",
        "-crf", str(crf),
        "-c:a", "aac",
        "-b:a", audio_bitrate,
        "-movflags", "+faststart",
        "-t", f"{audio_duration}",
        str(Path("output") / video_name),
    ]

    if print_mode:
        subprocess.run(cmd, check=True, cwd=str(project_root))
    else:
        subprocess.run(
            cmd,
            check=True,
            cwd=str(project_root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    return str(Path("output") / video_name)