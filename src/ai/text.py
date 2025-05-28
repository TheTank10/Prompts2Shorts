# Text is generated using the pollinations API: https://github.com/pollinations/pollinations

import json
from pathlib import Path
import requests
import random
import math

endpoint="https://text.pollinations.ai/openai"

def load_system_prompt(filename="base.txt"):
    return open(Path("data/prompts") / filename, "r").read()

def build_payload(prompt, model="openai-large", seed=-1, private=True, system_prompt="base.txt"):
    if system_prompt:
        system = load_system_prompt(filename=system_prompt)
    else: 
        system = ""

    msgs = [
        {"role": "system", "content": system},
        {"role": "user",   "content": f"Story Prompt: {prompt}"}
    ]
    return {
        "model": model,
        "messages": msgs,
        "seed": seed,
        "private": private,
        "tools": [{"type": "web_search_preview"}] if model == "searchgpt" else None,
    }

def generate(prompt, generate_json=True, settings=None):

    seed = str(settings["seed"])
    model = settings["text_model"]

    if seed == "-1":
        seed = str(math.floor(random.random() * 1000000))

    payload = build_payload(prompt, model=model, seed=seed, system_prompt=settings["system_prompt"]+".txt" if generate_json else None)
    resp = requests.post(endpoint, json=payload,
    headers={"Content-Type":"application/json"})
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    return (json.loads(content), seed) if generate_json else (content, seed)