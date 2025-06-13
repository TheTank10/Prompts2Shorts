from src import templates 
from src import utils
from src import ai
from pathlib import Path
import json
import os
import argparse

if not os.path.exists("temp"):
    os.makedirs("temp")
    
if not os.path.exists("output"):
    os.makedirs("output")

def str2bool(v):
    if isinstance(v, bool):
        return v
    val = v.lower().strip()
    if val in ("yes", "y", "true", "t", "1"):
        return True
    elif val in ("no", "n", "false", "f", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError(f"Boolean value expected (got '{v}').")    

def main():
    parser = argparse.ArgumentParser(prog="script")
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-c", "--create",
        action="store_true",
        help="Create a video."
    )
    group.add_argument(
        "--cleartemp",
        action="store_true",
        help="Clear the temp folder."
    )
    group.add_argument(
        "--getmodels",
        action="store_true",
        help="Get a list of pollinations ai text/image models. (json file with the information will be created to src/ai/pollination_models)"
    )
    group.add_argument(
        "--downloadffmpeg",
        action="store_true",
        help="Attempts to download an ffmpeg version subitable for this program and your OS."
    )
    parser.add_argument(
        "-p", "--prompt",
        type=str,
        help="Prompt text."
    )
    parser.add_argument(
        "-ps", "--prompts",
        type=str,
        help="Prompts file. The txt file contains prompts separated by ';'"
    )
    parser.add_argument(
        "-t", "--template",
        type=str,
        default="ai",
        help="The template to use for video generation. Current templates: 'ai', 'duckduckgo'"
    )
    parser.add_argument(
        "-pr", "--print",
        type=str2bool,
        default=True,
        help="Prints to the console as the video is being created."
    )
    parser.add_argument(
        "-rt", "--retries",
        type=int,
        default=5,
        help="How many times to retry if the video/image/audio generation fails."
    )
    parser.add_argument(
        "-st", "--settings",
        type=str,
        default="default",
        help="The JSON settings file to use for the video generator. Only include the name do not include the .json extension."
    )
    parser.add_argument(
        "-em", "--editmode",
        type=str2bool,
        default=False,
        help="Edit prompts and images as they are being generated. Useful to enhance your video."
    )

    args = parser.parse_args()

    if args.create:
        if not args.prompt and not args.prompts:
            parser.error("--prompt='' or --prompts='' is required when using --create")

        utils.authenticate_ffmpeg()

        print_mode = args.print
        video_settings = args.settings

        if args.prompts:
            with open(args.prompts, 'r') as file:
                prompts = file.read().split(';')
            if not prompts:
                parser.error("No prompts found in the provided file.")
        else: 
            prompts = [args.prompt]

        for i, prompt in enumerate(prompts):
            prompt = prompt.strip()

            video, seed = templates.prompt_to_short.generate(prompt, template=args.template, print_mode=print_mode, retries=args.retries, video_settings=video_settings, edit_mode=args.editmode)
           
            if video: 
                video_path = utils.rename_file(video, str(seed))
                print(f"Video {i+1}/{len(prompts)} has been generated into: {video_path}")
            else: 
                print(f"Video could not be generated. This could be due to many reasons including the API refusing your calls, errors with ffmpeg, setting an unsupported template and other common issues.\nCheck the common issues section in the readme file.\nVideo prompt: {prompt}")

            utils.clear_temp()
        
    elif args.cleartemp:
        utils.clear_temp()
        print("Temp folder cleared")

    elif args.getmodels:
        ai.pollination_models.update_model_list.list_text_models()
        ai.pollination_models.update_model_list.list_image_models()

        print("Text models list created to src/ai/pollination_models/pollination_text_models.json")
        print("Image models list created to src/ai/pollination_models/pollination_image_models.json")

    elif args.downloadffmpeg:
        ffmpeg_path = utils.download_ffmpeg()

        with open(Path("data/settings/ffmpeg.json"), 'w') as f: 
            json.dump({"path":str(ffmpeg_path)}, f, indent=4)

        print("* Authenticating FFmpeg...")
        utils.authenticate_ffmpeg()
        print("* FFmpeg downloaded and authenticated. You can now use --create.")

if __name__ == "__main__":
    main()