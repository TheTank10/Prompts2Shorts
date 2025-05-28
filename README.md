# prompts2shorts

**prompts2shorts** is a Python-based tool that converts your text prompts into AI-generated short-form videos for platforms like TikTok, YouTube Shorts, Instagram Reels, and more. It leverages generative AI models to produce visuals, audio, and video edits, fully automated via command-line.

---

## 🔧 Features

* 🎥 Generate short videos from a single prompt
* 🧠 Vast amount of completely free AI models that require no API key
* ⚙️ Highly customizable video generation settings
* ⚡ CUDA/GPU acceleration supported

---

## 🚀 Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/TheTank10/Prompts2Shorts.git
cd prompts2shorts
pip install -r requirements.txt
```

You also **must install [FFmpeg](https://www.ffmpeg.org/download.html)**. When you first run with `--create`, the program will prompt you to specify the FFmpeg executable path. If it's already added to your system's PATH, you can just enter `ffmpeg`.

---

## 🛠️ Usage

Run the program via command line with one of the available options:

### 🎮 Create a Video

```bash
# Create a single video in the command line with a prompt
python -m prompts2shorts --create --prompt="A video about anything you want"
# Optionally you can run __main__.py from the root directory
python __main__.py --create --prompt="A video about anything you want"

# Create multiple videos with different prompts from a text file. 
# Each prompt in the text file must be split by ';'
python -m prompts2shorts --create --prompts="example_prompts.txt"
```

**Optional Flags:**

* `-st`, `--settings`: Use a custom video settings file from `data/settings/video_settings/`. Do not include the `.json` extension.

  ```bash
  --settings="my_custom_config"
  ```

  Default: `data/settings/video_settings/default.json`
  Example path: `data/settings/video_settings/my_custom_config.json`

* `-rt`, `--retries`: Number of retries if generation fails (default: 5)
* `-pr`, `--print`: Whether to show logs in the console during video generation (default: True)
* `-em`, `--editmode`: Allows you to edit content text and image prompts while the video is being generated. Allows for higher quality videos even more using --enhance. (default: False)

To learn how to customize your video settings or create your own, refer to the `SETTINGS REFERENCE.md` file inside `data/settings/video_settings/`.

Run the -h flag for more information.

### 🧹 Clear Temporary Files

```bash
python -m prompts2shorts --cleartemp
```

This deletes files in the temporary folder. Normally this happens automatically after a video is successfully generated, but you can run this manually if something went wrong and temporary files were left over.

### 📦 Update AI Model List

```bash
python -m prompts2shorts --getmodels
```

Gets a list of the latest AI models from Pollinations and saves them as:

* `src/ai/pollination_models/pollination_text_models.json`
* `src/ai/pollination_models/pollination_image_models.json`

---

## ⚙️ Custom Settings

Video generation is highly customizable via the `data/settings/video_settings/` directory. You can:

* Create your own JSON config files for rendering
* Set parameters such as resolution, frame rate, font, and subtitle behavior
* Swap image/text models used in generation

> 📃 Refer to `SETTINGS REFERENCE.md` in `data/settings/video_settings/` for detailed descriptions of every setting.

---

## 🧠 System Prompts

The behavior of AI generation can be influenced using system prompts, located in:

```
data/prompts/
```

You can:

* Modify existing templates
* Create your own for different creative results

> 📃 Read the reference guide in `data/prompts/` to learn how to format and structure these prompts.

---

## 💻 Modifying the Code

This project is designed to be easily customizable, giving you full control over how text, image, and audio content is generated. Whether you want to use your own APIs (e.g., OpenAI, ElevenLabs) or switch to local models, you can modify the generation process with minimal effort.

### What You Can Customize:

* **Text/Image/Audio Generation:** Swap out Pollinations API calls for your preferred services or local models.
* **Subtitle Logic:** Change how subtitles are generated, styled, or timed.

### Where to Modify:

All core functionality is modularized under the `src` directory. Each submodule follows a consistent structure, making it easy to identify and edit specific functionality.

#### Example: Text Generation

To modify how text is generated:

* Navigate to: `src/ai/text.py`
* Edit the `generate` function:

  ```python
  def generate(prompt, generate_json=True, settings=None):
      # Your custom logic here
  ```

  This function should return plain text. If `generate_json=True`, the plain text will be transformed into a structured list used for building video scenes. How this text is generated or where you get it from is for you to customize. Currently all text/images/audio is generated using pollinations.ai

#### Other Modules

You can follow the same pattern to modify:

* `src/ai/image.py` – image generation
* `src/ai/audio.py` – voice generation
* `src/captions/srt.py` and `src/captions/ass.py` – subtitle generation

Each module has a single entry-point function (usually named `generate`) that you can replace or extend with your own logic.

Modules under `src/video/` can be modified similarly but do note that ffmpeg is pretty hard to work with.
---

## ❗ Common Issues

* **Missing FFmpeg**: Make sure `ffmpeg` is installed and accessible from your system's PATH or provide the full path to the executable when prompted.
* **API Failures**: The Pollinations API may rate-limit or fail randomly. Retry after some time.
* **Empty Output**: Sometimes the AI may not generate usable media. Tweak your prompt or try again.
* **gptimage requires an API key**: As of today gptimage requires of an API key from pollinations.ai