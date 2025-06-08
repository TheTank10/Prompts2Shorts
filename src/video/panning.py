import json
import subprocess
from pathlib import Path
import random
from src import utils 

effects = ["zoomin", "zoomout", "panright", "panleft", "panup", "pandown"]

ffmpeg = json.load(open(Path("data/settings/ffmpeg.json")))["path"]

def generate(
    image_path, 
    duration, 
    video_name = "effect.mp4", 
    video_index = 0, 
    crf = 28, 
    settings = None, 
    print_mode = True
):
    codec = utils.codec.get_codec()
    settings = settings or {}
    fps = settings.get("fps", 25)
    res_w, res_h = map(int, settings.get("resolution", "1080x1920").split("x"))
    total_frames = int(duration * fps)
    effect = settings.get("zoompan_effect", "random")
    effect = effect.split(",") if "," in effect else [effect]
    effect = effect[video_index] if len(effect) >= video_index+1 else effect[0]

    if effect == "random":
        effect = random.choice(effects)

    if not effect in effects: 
        raise f"{effect} not a valid zoompan effect."

    # hidden settings
    max_zoom = settings.get("zoompan_max_zoom", 1.5)
    canvas_w = settings.get("zoompan_canvas_width", 8000)

    # compute dynamic speeds
    zoom_delta = (max_zoom - 1) / total_frames
    pan_dist = max((canvas_w / max_zoom) - res_w, 0)
    pan_speed = pan_dist / total_frames
    pan_vdist = max((canvas_w / max_zoom) - res_h, 0)
    pan_vspeed = pan_vdist / total_frames

    if effect == "zoomin":
        vf = (
            f"scale={canvas_w}:-1,"
            f"zoompan=z='min(zoom+{zoom_delta},{max_zoom})':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={total_frames}:s={res_w}x{res_h}:fps={fps},"
            f"format=yuv420p"
        )
    elif effect == "zoomout":
        start_zoom = max_zoom  # e.g., 1.5
        zoom_speed = (max_zoom - 1.0) / total_frames

        vf = (
            f"scale={canvas_w}:-1,"
            f"zoompan="
            f"z='if(eq(on,0),{start_zoom},max(zoom-{zoom_speed},1.0))':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={total_frames}:"
            f"s={res_w}x{res_h}:fps={fps},"
            "format=yuv420p"
        )
    else:
        # pan variations
        if effect == "panright":
            x_exp = f"if(lt(on*{pan_speed},iw/zoom-out_w),(iw/2-iw/zoom/2)+on*{pan_speed},iw/zoom-out_w)"
            y_exp = "ih/2-ih/zoom/2"
        elif effect == "panleft":
            x_exp = f"if(lt(on*{pan_speed},iw/zoom-out_w),(iw/2-iw/zoom/2)-on*{pan_speed},0)"
            y_exp = "ih/2-ih/zoom/2"
        elif effect == "panup":
            x_exp = "iw/2-iw/zoom/2"
            y_exp = f"if(lt(on*{pan_vspeed},ih/zoom-out_h),(ih/2-ih/zoom/2)-on*{pan_vspeed},0)"
        elif effect == "pandown":
            x_exp = "iw/2-iw/zoom/2"
            y_exp = f"if(lt(on*{pan_vspeed},ih/zoom-out_h),(ih/2-ih/zoom/2)+on*{pan_vspeed},ih/zoom-out_h)"

        vf = (
            f"scale={canvas_w}:-1,"  
            f"zoompan=z='min(zoom+{zoom_delta},{max_zoom})':"
            f"d={total_frames}:"
            f"x='{x_exp}':"
            f"y='{y_exp}':"
            f"s={res_w}x{res_h}:fps={fps},"
            "format=yuv420p"
        )

    cmd = [
        ffmpeg,
        "-y",
        "-loop","1","-i",image_path,
        "-vf",vf,
        "-t",str(duration),
        "-c:v",codec,
        "-crf",str(crf),
        "-pix_fmt","yuv420p",
        str(Path("temp") / video_name)
    ]

    run_kwargs = {"check":True}
    if not print_mode:
        run_kwargs.update(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(cmd, **run_kwargs)
    return str(Path("temp") / video_name)