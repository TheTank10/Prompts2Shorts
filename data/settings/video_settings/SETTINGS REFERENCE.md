# Video Settings Guide

This guide explains each setting in the video settings file used to control how your videos are generated. These settings are saved in JSON format (like `default.json`) and can be customized for different projects. When no settings are provided when running the `--create` command, the `default.json` settings are automatically used `data/settings/video_settings/default.json`

To use a custom settings file, pass it into your command using:

```bash
--settings="mycustomsettings"  # or use the shorthand -st (do not include the json extension)
```

---

## Example Settings File

```json
{
    "text_model": "openai-large",
    "image_model": "flux",
    "text_to_speech_voice": "ash",
    "seed": -1,
    
    "resolution": "1080x1920",
    "fps": 25,
    "zoom_speed": 0.0010,
    "force_cuda": false,

    "font_name": "Montserrat Bold",
    "font_size": 20,
    "font_normal_color": "FFFFFF",
    "font_highlighted_color": "00FF00",
    "font_outline": 1,
    "font_shadow": 2,
    "font_alignment": "MIDDLE_CENTER",

    "subtitles": true,
    "subtitle_entry_ms": 250,
    "subtitle_init_scale_percentage": 90,
    "subtitle_final_scale_percentage": 100,

    "transition": "slideleft",
    "transition_duration": 0.3,

    "system_prompt": "base"
}
```

---

## Setting Descriptions

| Setting                           | Type   | Default             | Description                                                                                                                                                            |
| --------------------------------- | ------ | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `text_model`                      | string | `"openai-large"`    | AI model used for text generation (e.g. scriptwriting). Run `--getmodels` to list all available models.                                                                |
| `image_model`                     | string | `"flux"`            | AI model used for generating images. Some models like `gptimage` may require a key. Run `--getmodels` to list all available models.                                                                                    |
| `text_to_speech_voice` | string | `"ash"` | Voice used for text to speech generation. Options include: `"alloy"`, `"echo"`, `"fable"`, `"onyx"`, `"nova"`, `"shimmer"`, `"coral"`, `"verse"`, `"ballad"`, `"ash"`, `"sage"`, `"amuch"`, `"dan"`. Go to openai.fm to experiment |
| `seed`                            | int    | `-1`                | Random seed for consistency. Set to any number ≥ 0 to make outputs repeatable.                                                                                         |
| `resolution`                      | string | `"1080x1920"`       | Final video resolution (WIDTHxHEIGHT). `1080x1920` is ideal for vertical platforms like TikTok.                                                                        |
| `fps`                             | int    | `25`                | Frames per second for the video. Higher FPS = smoother motion.                                                                                                         |
| `zoom_speed`                      | float  | `0.0010`            | Controls how fast the camera zooms in each frame. 0 = no zoom.                                                                                                         |
| `force_cuda`                      | bool   | `false`             | Force usage of CUDA GPU acceleration. Only enable if you know your system supports CUDA.                                                                               |
| `font_name`                       | string | `"Montserrat Bold"` | Font used for subtitles. Must exist in `data/fonts/`.                                                                                                                  |
| `font_size`                       | int    | `20`                | Size of subtitle text.                                                                                                                                                 |
| `font_normal_color`               | string | `"FFFFFF"`          | Hex color code for normal subtitle text (white).                                                                                                                       |
| `font_highlighted_color`          | string | `"00FF00"`          | Color used to highlight specific words.                                                                                                                                |
| `font_outline`                    | int    | `1`                 | Thickness of the text outline (in pixels). Improves readability.                                                                                                       |
| `font_shadow`                     | int    | `2`                 | Depth of the shadow below the text.                                                                                                                                    |
| `font_alignment`                  | string | `"MIDDLE_CENTER"`   | Position of subtitles. Options: `TOP_LEFT`, `TOP_CENTER`, `TOP_RIGHT`, `MIDDLE_LEFT`, `MIDDLE_CENTER`, `MIDDLE_RIGHT`, `BOTTOM_LEFT`, `BOTTOM_CENTER`, `BOTTOM_RIGHT`. |
| `subtitles`                       | bool   | `true`             | Enables or disables subtitle display.                                                                                                                                  |
| `subtitle_entry_ms`               | int    | `250`               | Time (ms) each word takes to animate into view. Lower = faster.                                                                                                        |
| `subtitle_init_scale_percentage`  | int    | `90`                | Starting scale (%) when a subtitle word appears.                                                                                                                       |
| `subtitle_final_scale_percentage` | int    | `100`               | Final scale (%) once the word animation ends.                                                                                                                          |
| `transition`                   | string | `"random"`            | Transition effect used to transition between images. 31 effects to pick from. Read below for a list.| 
| `transition_duration`                   | int | `0.3`            | Duration (in seconds) the transition will last |
| `system_prompt`                   | string | `"base"`            | Internal system prompt used for AI generation. Should output a list like: `[{"content":"", "ai_image_query":"", "voice_style":""}]` Go to data/prompts/ to read more about how to create your own.                                   |

---

## 🎮 FFmpeg `xfade` Transition Effects Cheatsheet

| Transition      | Description                                           |
| --------------- | ----------------------------------------------------- |
| **random**      | Randomly choose between these effects                 |
| **fade**        | Crossfade between two videos.                         |
| **fadeblack**   | Fade through black between videos.                    |
| **fadewhite**   | Fade through white between videos.                    |
| **wipeleft**    | Wipe transition from right to left.                   |
| **wiperight**   | Wipe transition from left to right.                   |
| **wipeup**      | Wipe transition from bottom to top.                   |
| **wipedown**    | Wipe transition from top to bottom.                   |
| **slideleft**   | Slide transition from right to left.                  |
| **slideright**  | Slide transition from left to right.                  |
| **slideup**     | Slide transition from bottom to top.                  |
| **slidedown**   | Slide transition from top to bottom.                  |
| **circleopen**  | Circular opening transition revealing the next video. |
| **circleclose** | Circular closing transition hiding the current video. |
| **circlecrop**  | Circular crop transition between videos.              |
| **radial**      | Radial transition effect.                             |
| **diagtl**      | Diagonal transition from top-left to bottom-right.    |
| **diagtr**      | Diagonal transition from top-right to bottom-left.    |
| **diagbl**      | Diagonal transition from bottom-left to top-right.    |
| **diagbr**      | Diagonal transition from bottom-right to top-left.    |
| **hlslice**     | Horizontal slice transition from left to right.       |
| **hrslice**     | Horizontal slice transition from right to left.       |
| **vuslice**     | Vertical slice transition from top to bottom.         |
| **vdslice**     | Vertical slice transition from bottom to top.         |
| **smoothleft**  | Smooth transition moving leftward.                    |
| **smoothright** | Smooth transition moving rightward.                   |
| **smoothup**    | Smooth transition moving upward.                      |
| **smoothdown**  | Smooth transition moving downward.                    |
| **distance**    | Transition effect based on distance mapping.          |
| **pixelize**    | Pixelization effect during transition.                |
| **blurblack**   | Blur transition fading to black.                      |
| **blurwhite**   | Blur transition fading to white.                      |

---

## Tips for Customization

* **AI Model Selection:** Use larger models like `openai-large` or `deepseek-reasoning` for higher quality scripts. Use smaller ones (like `openai-fast`) for faster generation. Use image models like `flux` for balanced image making. Use faster image models like `turbo` for very quick image generation (perfect for NSFW by the way). `gptimage` as of this day requries a key you get from pollinations even tho they say that their services are supposed to be free and keyless... 
* **Consistent Results:** Set a `seed` value to generate consistent outputs with the same prompt.
* **Video Format:** Use `1080x1920` for vertical video. Use `1920x1080` for horizontal.
* **Text Visibility:** Tweak `font_size`, `font_outline`, and `font_shadow` for readability.
* **Color Styling:** Use [htmlcolorcodes.com](https://htmlcolorcodes.com/) to choose hex colors.
* **Subtitle Animation:** Lower `subtitle_entry_ms` to make words pop up quicker. Edit `subtitle_init_scale_percentage` to control the starting size of the subtitle when it first enters the video (set to 100 to disable)
* **CUDA Troubleshooting:** Set `force_cuda` to `true` only if you’re sure your system supports it. Otherwise, leave it `false` for automatic detection.

---

## Common Issues

**Font Not Found Error**

> This happens when the font name is incorrect or the font file is missing from `data/fonts/`. The name should match the font’s internal name, not the filename. Open the `.ttf` file to confirm the actual font name or upload it into a font website to get its actual internal name.

---

you can use the `--getmodels` command to view available text and image models provided by pollinations.ai.
