from src import templates 
from src import utils
from src import ai
import os
import argparse

if not os.path.exists("temp"):
    os.makedirs("temp")
    
if not os.path.exists("output"):
    os.makedirs("output")

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
        "-pr", "--print",
        type=bool,
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
        type=bool,
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
            video, seed = templates.prompt_to_short.generate(prompt, print_mode=print_mode, retries=args.retries, video_settings=video_settings, edit_mode=args.editmode)

            if video: 
                video_path = utils.rename_file(video, str(seed))
                print(f"Video {i+1}/{len(prompts)} has been generated into: {video_path}")
            else: 
                print(f"Video could not be generated. This could be due to many reasons including the API refusing your calls, errors with ffmpeg and other common issues.\nCheck the common issues section in the readme file.\nVideo prompt: {prompt}")

            utils.clear_temp()
        
    elif args.cleartemp:
        utils.clear_temp()
        print("Temp folder cleared")
    elif args.getmodels:
        ai.pollination_models.update_model_list.list_text_models()
        ai.pollination_models.update_model_list.list_image_models()

        print("Text models list created to src/ai/pollination_models/pollination_text_models.json")
        print("Image models list created to src/ai/pollination_models/pollination_image_models.json")
        
if __name__ == "__main__":
    main()