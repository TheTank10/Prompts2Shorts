import pysubs2
from pathlib import Path
import re

def get_highlighted_words(text):
    segments = re.findall(r"\*(.*?)\*", text)
    words = []
    for segment in segments:
        clean = re.sub(r"[^\w\s]", "", segment)
        words.extend(w.lower() for w in clean.split() if w)
    return words

def build_highlight_regex(words):
    clean_words = [re.sub(r"[^a-z]", "", word) for word in words]
    clean_words = [word for word in clean_words if word]
    if not clean_words:
        return re.compile(r"$^")  # Matches nothing
    pattern = r"\b(?:{})\b".format("|".join(map(re.escape, clean_words)))
    return re.compile(pattern, re.IGNORECASE)

def hex_to_ass_color(hex_color):
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")
    r, g, b = hex_color[:2], hex_color[2:4], hex_color[4:]
    return f"&H{b}{g}{r}&"

def generate(srt_file_path, transcript, ass_file_name="ass_output.ass", settings=None):
    if settings["subtitles"] == False:
        return None

    # Get highlighted words and regex
    highlighted_words = get_highlighted_words(transcript)
    highlight_re = build_highlight_regex(highlighted_words)

    # Load subtitles
    subs = pysubs2.load(srt_file_path, encoding="utf-8")

    # Set up default style
    default_style = subs.styles.get("Default", pysubs2.SSAStyle())
    default_style.fontname = settings["font_name"]
    default_style.fontsize = settings["font_size"]
    default_style.primarycolor = pysubs2.Color(255, 255, 255)  # White
    default_style.outline = settings["font_outline"]
    default_style.shadow = settings["font_shadow"]
    default_style.alignment = pysubs2.Alignment[settings["font_alignment"]]
    subs.styles["Default"] = default_style

    green_color = hex_to_ass_color(settings["font_highlighted_color"])
    normal_color = hex_to_ass_color(settings["font_normal_color"])
    green_tag = f"{{\\1c{green_color}}}"
    reset_tag = f"{{\\1c{normal_color}}}"

    # Animation config
    entry_ms = settings["subtitle_entry_ms"]
    init_scale = settings["subtitle_init_scale_percentage"]
    final_scale = settings["subtitle_final_scale_percentage"]
    animation_tag = f"{{\\fscx{init_scale}\\fscy{init_scale}\\t(0,{entry_ms},\\fscx{final_scale}\\fscy{final_scale})}}"

    for line in subs:
        raw_text = line.text.replace("*", "")
        colored_text = highlight_re.sub(lambda m: f"{green_tag}{m.group(0)}{reset_tag}", raw_text)
        line.text = animation_tag + colored_text

    output_path = Path("temp") / ass_file_name
    subs.save(str(output_path))
    return str(output_path)
