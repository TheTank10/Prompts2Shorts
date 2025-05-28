import subprocess
import tempfile
from pathlib import Path
import json

ffmpeg = json.load(open(Path("data/settings/ffmpeg.json")))["path"]

# Determine project root (two levels up from this file)
project_root = Path(__file__).resolve().parents[2]

def make_concat_list(video_list):
    f = tempfile.NamedTemporaryFile(
        mode='w', delete=False, suffix='.txt', dir=str(project_root)
    )
    for v in video_list:
        f.write(f"file '{v}'\n")
    f.close()
    return Path(f.name)


def escape_colons(path: str) -> str:
    return path.replace(':', '\\:')

def generate(
    video_list,
    audio_path,
    ass_file,
    video_name='final_video.mp4',
    crf=28,
    audio_bitrate='96k',
):
    list_file = make_concat_list(video_list)

    output = str(Path("output") / video_name)

    try:
        if ass_file:
            ass_escaped = escape_colons(str(Path(ass_file).as_posix()))
            fonts_dir = 'data/fonts'
            vf_arg = f"format=yuv420p,ass={ass_escaped}:fontsdir={fonts_dir}"
            vf_args = ['-vf', vf_arg]
        else:
            vf_args = []

        cmd = [
            ffmpeg,
            '-y',
            '-f', 'concat', '-safe', '0', '-i', str(list_file),
            '-i', audio_path,
            *vf_args,
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', str(crf),
            '-c:a', 'aac', '-b:a', audio_bitrate,
            '-movflags', '+faststart',
            output
        ]

        subprocess.run(
            cmd,
            check=True,
            cwd=str(project_root)
        )

    finally:
        if list_file.exists():
            list_file.unlink()

    return output