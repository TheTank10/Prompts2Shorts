# Template for generating videos completely from AI

from src import ai 
from src import captions 
from src import video
import re
import time
import json
from pathlib import Path
from PIL import Image

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

def edit_image(ai_image_query, content_length, image_index, settings, retries):
    ai_image_path = None 

    while True:
        try:
            ai_image_path = ai.image.generate(ai_image_query, image_name=f"image_{image_index}.jpg", settings=settings)
            break
        except Exception as e:
            print("Error re-generating image. Retrying...", e)
            retries-=1
            if retries==0:
                return

    print(f"Edit image prompt:\n\nPart {image_index+1}/{content_length}: {ai_image_query}\n\nEdit the prompt of the ai image or press enter to continue.\nUse --enhance ... to enhance this prompt with AI")
    image = Image.open(ai_image_path)
    image.show()
    edit = input(": ")

    
    if edit=="":
        return ai_image_path
    else:
        return edit_image(edit, content_length, image_index, settings, retries)

def generate(prompt, print_mode=True, edit_mode=False, retries=5, video_settings="default"):

    settings = json.load(open(Path(f"data/settings/video_settings/{video_settings}.json")))
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
            print(f"Fetching ai image and ai audio for story part {i+1}/{story_length}. time elapsed: ", time.time()-tick)

        content = part["content"]
        content = re.sub(r'[\*\(\)]', '', content)
        ai_image_query = part["ai_image_query"]
        voice_style = part["voice_style"]

        if edit_mode:
            content = edit_text(content, story_length, i, settings, retries)
            if not content:
                return 0,0
        
        story_transcript += content+" "
        ai_image_path = None 
        audio_path, duration = None, None
        image_video_path = None

        while not ai_image_path or not audio_path:
            try:
                if ai_image_path is None:
                    if edit_mode: 
                        ai_image_path = edit_image(ai_image_query, story_length, i, settings, retries)
                        if ai_image_path==None: 
                            return 0,0
                    else:
                        ai_image_path = ai.image.generate(ai_image_query, image_name=f"image_{i}.jpg", settings=settings)
                if audio_path is None: 
                    audio_path, duration = ai.audio.generate(content, "echo", voice_style, audio_name=f"audio_{i}.mp3")
                image_video_path = video.panning.generate(ai_image_path, duration, video_name=f"panning_video{i}.mp4", settings=settings)
                retries = max_retries
            except Exception as e:
                print("Error generating image, audio or/and video. Retrying...", e)
                ai_image_path = None
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

    final_video = video.stitch.generate(videos, concatenated_audio, ass_file, settings=settings)

    return final_video, story_seed