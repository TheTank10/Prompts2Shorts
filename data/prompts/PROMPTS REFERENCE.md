# Custom System Prompts Guide

This guide will help you craft and manage your own system prompts for **prompts2shorts**, ensuring your AI generates scripts and image queries exactly the way you want.

---

## 1. What is a System Prompt?

A **system prompt** tells the AI how to behave when converting/generating your story into a JSON list of objects. Each object must include three keys:

* `content`: the script text to be spoken in the video.
* `ai_image_query`: a concise, vivid scene description for image generation.

Without these three keys, the AI output will not be parsed correctly by prompts2shorts.
YOU MUST include these rules in your system prompt.
---

## 2. Default (`base.txt`)

The default prompt is located at `data/prompts/base.txt`:

```txt
You are a creative video script writer for short-form YouTube Shorts.
Your job is to turn the user’s story prompt into a JSON list of objects.
Each object must have two keys:
- content: the script text
- ai_image_query: a short, vivid scene description

Content rules:
• No emojis  
• Use simple, clear language  
• Wrap important *single words* (not phrases) in asterisks

Image query rules:
• Be concise but detailed  
• Specify style (e.g. cinematic, watercolor)  
• Specify mood (e.g. eerie, joyful)  
• Specify composition (e.g. close-up, wide-angle)  
• Specify lighting (e.g. golden hour, backlit)  
• Use a simple color palette (e.g. muted earth tones)

Response rules:
• Return only the JSON list—no extra text  
• Follow the user’s prompt exactly
```

You can use this as a starting point or copy it to create your own variation.

---

## 3. Creating Your Own Prompt

1. **Copy** `base.txt` and rename it (e.g. `dramatic_narrator.txt`).
2. **Edit** the content to customize:
   * Tweak **content rules** (e.g. "avoid superlatives").
   * Modify **image query rules** (e.g. "focus on pastel color schemes").
3. **Ensure** you still instruct the AI to output a JSON list of objects with exactly `content` and `ai_image_query`

**Example snippet**:

```txt
# At top of your file
You are a theatrical narrator, delivering epic mini-stories.
Your output MUST be a JSON array of objects, each with keys: content and ai_image_query

# Keep content & image query rules from base.txt...
```

---

## 4. Activating a Custom Prompt

1. Open your video settings JSON in `data/video_settings/`.
2. Find the `system_prompt` field and set it to your new filename (without path), e.g.:

```json
{
  "text_model": "openai-large",
  "image_model": "flux",
  "system_prompt": "dramatic_narrator",
  …
}
```

3. Run your command as usual. The AI will now use your custom system prompt.

---

## 5. Tips for Better Prompts

* **Be explicit**: The more detail you give, the more consistent your results.
* **Test iteratively**: Small tweaks help you hone in on the right mood without overloading the AI.
* **Add rules**: Adding rules allows you to control how the AI will generate your videos. Some examples include rules such as don't include people or animals in AI images, Don't generate NSFW content, etc..
* **Keep JSON structure**: If you remove or rename keys, prompts2shorts won’t be able to parse the output.
---