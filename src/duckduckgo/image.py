from duckduckgo_search import DDGS
import requests
from PIL import Image
from io import BytesIO
import os

def generate(
    prompt,
    image_name = "ddg_image.png",
    settings=None,
    max_results=5,
):
    
    resolution = settings.get("resolution", "1080x1920")

    out_folder="temp"
    w0, h0 = map(int, resolution.split("x"))

    best_size = 0
    best_img  = None

    with DDGS() as ddgs:
        # use DuckDuckGo filters: Large, Tall, photo
        results = ddgs.images(
            keywords=prompt,
            region="us-en",
            safesearch="off",
            size="Large",        
            layout="Tall",       
            type_image="photo",  
            max_results=max_results,
        )

        for item in results:
            try:
                resp = requests.get(item["image"], timeout=5)
                data = resp.content
                # pick the highest-byte-size image
                if len(data) > best_size:
                    best_size = len(data)
                    best_img  = Image.open(BytesIO(data)).convert("RGB")
            except:
                continue

    if best_img is None:
        return None

    scale = max(w0 / best_img.width, h0 / best_img.height)
    nw, nh = int(best_img.width * scale), int(best_img.height * scale)
    img = best_img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w0) // 2, (nh - h0) // 2
    crop = img.crop((left, top, left + w0, top + h0))

    out_path = os.path.join(
        out_folder,
        image_name
    )
    crop.save(out_path, "PNG")
    return out_path