# Images are generated using the pollinations API: https://github.com/pollinations/pollinations

import requests
from urllib.parse import quote_plus
from pathlib import Path

"""
    Args:
      prompt (str):      Text description of the image.
      output_path (str): Where to save the downloaded image.
      model (str):       Image model to use (default "flux").
      seed (int|None):   Seed for reproducible results.
      width (int):       Image width (default 1024).
      height (int):      Image height (default 1024).
      nologo (bool):     Disable Pollinations logo overlay if True.
      private (bool):    Prevent public feed posting if True.
      enhance (bool):    Enhance the prompt via LLM if True.
      safe (bool):       Strict NSFW filtering if True.
      referrer (str|None): Optional referrer identifier.
"""

def generate(
    prompt,
    image_name="output_image.png",
    seed=None,
    width=1080,
    height=1920,
    nologo=True,
    private=True,
    enhance=True,
    safe=False,
    referrer=None,
    settings=None,
):
    encoded_prompt = quote_plus(prompt)
    base = f"https://image.pollinations.ai/prompt/{encoded_prompt}"

    model = settings.get("image_model", "flux")

    params = {
        "model": model,
        "width": width,
        "height": height,
        "nologo": str(nologo).lower(),
        "private": str(private).lower(),
        "enhance": str(enhance).lower(),
        "safe": str(safe).lower(),
        "negative_prompt": ", negative prompt: worst quality, blurry",
        "token": "desktophut"
    }
    if seed is not None:
        params["seed"] = seed
    if referrer:
        params["referrer"] = referrer

    resp = requests.get(base, params=params)
    resp.raise_for_status()

    image_path = str(Path("temp") / image_name)

    with open(image_path, "wb") as f:
        f.write(resp.content)

    return image_path