# Template for generating videos using duckduckgo images and AI scripts

from src import ai
from src import duckduckgo
from src import captions 
from src import video
import re
import time
import json
from pathlib import Path
#from PIL import Image 

def edit_text(content, content_length, content_index, settings, retries):
    print(f"Edit content:\n\nPart {content_index+1}/{content_length}: {content}\n\nEdit this part of the content or press enter to continue.\nUse --enhance ... to enhance with AI")
    edit = input(": ")

    if edit.split(" ")[0]=="--enhance":
        while True:
            try:
                content, _ = ai.text.generate(f"Enhance this: {content}\n\n{edit.partition(' ')[2]}", generate_json=False, settings=settings)
                return edit_text(content, content_length, content_index, settings, retries)
            except Exception as e: 
                print("Error re-generating content. Retrying...", e)
                retries-=1
                if retries==0:
                    return
    elif edit!="":
        return edit
    else: 
        return content
    
# TODO: edit_image for ddg sourced images

def generate(prompt, print_mode=True, edit_mode=False, retries=5, video_settings="default"):
    settings = json.load(open(Path(f"data/settings/video_settings/{video_settings}.json")))

    if settings.get("system_prompt", "base") == "base": 
        settings["system_prompt"] = "base_ddg"

    text_to_speech_voice = settings.get("text_to_speech_voice", "ash")

    max_retries = retries
    tick = time.time()

    if print_mode:
        print("Generating story. time elapsed: ", time.time()-tick)

    story, story_seed = None, None
    story_transcript = "" 

    while not story:
        try:
            story, story_seed = ai.text.generate(prompt, settings=settings)
            retries = max_retries
        except Exception as e: 
            print("Error generating story. Retrying...", e)
            story = None
            retries -= 1
            if retries <= 0:
                return 0,0
            time.sleep(1)

    story_length = len(story)
    videos = []
    audios = []

    for i, part in enumerate(story):

        if print_mode:
            print(f"Fetching DuckDuckGo image and ai audio for story part {i+1}/{story_length}. time elapsed: ", time.time()-tick)

        content = part["content"]
        story_transcript += content+" "
        
        content = re.sub(r'[\*\(\)]', '', content)
        google_image_query = part["google_image_query"]
        
        if edit_mode:
            content = edit_text(content, story_length, i, settings, retries)
            if not content:
                return 0,0

        google_image_path = None 
        audio_path, duration = None, None
        image_video_path = None

        while not google_image_path or not audio_path:
            try:
                if google_image_path is None:
                    google_image_path = duckduckgo.image.generate(google_image_query, image_name=f"image_{i}.png", settings=settings)
                if audio_path is None: 
                    audio_path, duration = ai.audio.generate(content, text_to_speech_voice, audio_name=f"audio_{i}.mp3")
                image_video_path = video.panning.generate(google_image_path, duration, video_name=f"panning_video{i}.mp4", settings=settings, print_mode=print_mode)
                retries = max_retries
            except Exception as e:
                print("Error fetching image, audio or/and video. Retrying...", e)
                google_image_path = None
                audio_path = None
                retries -= 1
                if retries <= 0:
                    return 0,0
                time.sleep(1)

        videos.append(image_video_path)
        audios.append(audio_path)

    if print_mode:
        print("Concatinating audio, generating srt and ass file. time elapsed: ", time.time()-tick)

    concatenated_audio = video.audio.concatenate_audio(audios, audio_name="final_audio.mp3")
    srt_file = captions.srt.generate(concatenated_audio, story_transcript, srt_file_name="words.srt")
    ass_file = captions.ass.generate(srt_file, story_transcript, ass_file_name="words.ass", settings=settings)

    if print_mode:
        print("Stiching video together. time elapsed: ", time.time()-tick)

    final_video = video.stitch.generate(videos, concatenated_audio, ass_file, settings=settings, print_mode=print_mode)

    return final_video, story_seed