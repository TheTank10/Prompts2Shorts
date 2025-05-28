from forcealign import ForceAlign
from pathlib import Path
import nltk
from nltk.data import find

nltk_resources = [
    "taggers/averaged_perceptron_tagger",
    "taggers/averaged_perceptron_tagger_eng"
]

for resource in nltk_resources:
    try:
        find(resource)
    except LookupError:
        print(f"nltk {resource} not found. Downloading...")
        nltk.download(resource.split("/")[-1])

def format_timestamp(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace('.', ',')

def write_srt(words, srt_file_name, words_per_caption=1):
    path = Path("temp") / srt_file_name

    with open(path, 'w', encoding='utf-8') as f:
        idx = 1
        buffer = []
        start = None
        end = None

        for w in words:
            if start is None:
                start = w.time_start
            buffer.append(w.word)
            end = w.time_end

            if len(buffer) >= words_per_caption:
                f.write(f"{idx}\n")
                f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
                f.write(" ".join(buffer) + "\n\n")
                idx += 1
                buffer = []
                start = None

        if buffer:
            f.write(f"{idx}\n")
            f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
            f.write(" ".join(buffer) + "\n")

def generate(audio_path, transcript, srt_file_name="srt_output.srt"):
    align = ForceAlign(audio_file=audio_path, transcript=transcript)
    words = align.inference()
    write_srt(words, srt_file_name)
    return str(Path("temp") / srt_file_name)