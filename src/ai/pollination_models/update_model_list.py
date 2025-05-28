import json
import requests
from pathlib import Path

def list_text_models():
    script_dir = Path(__file__).parent
    output_file = script_dir / "pollination_text_models.json"
    resp = requests.get("https://text.pollinations.ai/models")
    resp.raise_for_status()
    data = resp.json()

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def list_image_models():
    script_dir = Path(__file__).parent
    output_file = script_dir / "pollination_image_models.json"
    resp = requests.get("https://image.pollinations.ai/models")
    resp.raise_for_status()
    data = resp.json()

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)