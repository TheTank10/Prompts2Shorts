from pathlib import Path
from PIL import Image
import re
import time
import json

from src import ai
from src import duckduckgo
from src import captions
from src import video

SUPPORTED_QUERIES = ["ai_image_query", "google_image_query"]

def prompt_for_text_edit(text, index, length, settings, retries):
    print(f"Prompt used for part {index+1}/{length}:\n{text}\n")
    print("Enter new text directly, or use '--enhance <instructions>' to have AI improve the original prompt.")
    print("Press enter if you do not wish to edit.")
    user_input = input(": ")

    if user_input.startswith("--enhance"):
        instructions = user_input.partition(' ')[2]
        try:

            enhanced_text, _ = ai.text.generate(
                f"Text to enhance: {text}\n\n{instructions}",
                generate_json=False,
                settings=settings,
            )

            return prompt_for_text_edit(enhanced_text, index, length, settings, retries)
        except Exception:

            if retries > 0:
                return prompt_for_text_edit(text, index, length, settings, retries - 1)

    return user_input or text

def prompt_for_image_edit(query, index, length, settings, retries, query_type):

    print(f"Image prompt for part {index+1}/{length} ({query_type}):\n{query}\n")
    try:
        if query_type == "ai_image_query":
            image_path = ai.image.generate(
                query,
                image_name=f"image_{index}.jpg",
                settings=settings,
            )
        elif query_type == "google_image_query":
            image_path = duckduckgo.image.generate(
                query,
                image_name=f"image_{index}.png",
                settings=settings,
            )
        Image.open(image_path).show()

        user_prompt = input(
            f"Part {index+1}/{length}: adjust image prompt or press enter to accept:\n: "
        )
        if user_prompt:
            return prompt_for_image_edit(user_prompt, index, length, settings, retries, query_type)
        return image_path

    except Exception:
        if retries > 0:
            return prompt_for_image_edit(query, index, length, settings, retries - 1, query_type)
        return query

def generate(
    prompt,
    template="ai",
    print_mode=True,
    edit_mode=False,
    retries=5,
    video_settings="default",
):
    # load settings
    settings_file = Path(f"data/settings/video_settings/{video_settings}.json")
    config = json.loads(settings_file.read_text())

    # adjust system prompt for duckduckgo
    if template == "duckduckgo" and config.get("system_prompt") == "base":
        config["system_prompt"] = "base_ddg"

    voice = config.get("text_to_speech_voice", "ash")
    max_retries = retries
    start_time = time.time()

    if print_mode:
        print("Generating story. Elapsed:", time.time() - start_time)

    # generate story sections
    story, seed = None, None
    while not story and retries:
        try:
            story, seed = ai.text.generate(prompt, settings=config)
            retries = max_retries
        except Exception:
            retries -= 1
            time.sleep(1)
    if not story:
        return 0, 0

    total_parts = len(story)
    video_clips = []
    audio_clips = []
    transcript = ""

    for i, part in enumerate(story):
        if print_mode:
            print(f"Part {i+1}/{total_parts}. Elapsed:", time.time() - start_time)

        # clean up text
        raw_content = part["content"]
        clean_content = re.sub(r"[()*]", "", raw_content)
        transcript += raw_content + " "  # build transcript string

        # allow text edits
        if edit_mode:
            clean_content = prompt_for_text_edit(
                clean_content, i, total_parts, config, retries
            )

        # detect which query field is present
        for key in SUPPORTED_QUERIES:
            if key in part:
                query_text = part[key]
                query_key = key
                break
        else:
            query_text = ""
            query_key = ""

        img_path = None
        audio_path = None
        duration = None

        while (not img_path or not audio_path) and retries:
            try:
                # image generation
                if not img_path:
                    if edit_mode:
                        img_path = prompt_for_image_edit(
                            query_text, i, total_parts, config, retries, query_key
                        )
                    elif key == "ai_image_query":
                        img_path = ai.image.generate(
                            query_text,
                            image_name=f"image_{i}.jpg",
                            settings=config,
                        )
                    else:
                        img_path = duckduckgo.image.generate(
                            query_text,
                            image_name=f"image_{i}.png",
                            settings=config,
                        )

                # audio generation
                if not audio_path:
                    audio_path, duration = ai.audio.generate(
                        clean_content, voice, audio_name=f"audio_{i}.mp3"
                    )

                # create panning video clip
                clip = video.panning.generate(
                    img_path,
                    duration,
                    video_name=f"panning_video{i}.mp4",
                    video_index=i,
                    settings=config,
                    print_mode=print_mode,
                )
                video_clips.append(clip)
                audio_clips.append(audio_path)
                retries = max_retries

            except Exception as e:
                print("Error fetching image or audio: ", e)
                retries -= 1
                img_path, audio_path = None, None
                time.sleep(1)

        if retries == 0:
            return 0, 0

    if print_mode:
        print("Concatenating, generating captions. Elapsed:", time.time() - start_time)

    # combine audio and generate subtitles
    audio_all = video.audio.concatenate_audio(audio_clips, audio_name="final_audio.mp3")
    srt_file = captions.srt.generate(audio_all, transcript, srt_file_name="words.srt")
    ass_file = captions.ass.generate(srt_file, transcript, ass_file_name="words.ass", settings=config)

    if print_mode:
        print("Stitching video. Elapsed:", time.time() - start_time)

    final_video = video.stitch.generate(
        video_clips, audio_all, ass_file, settings=config, print_mode=print_mode
    )
    return final_video, seed