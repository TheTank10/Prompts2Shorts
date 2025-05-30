# Custom System Prompts Guide

This guide will help you craft and manage your own system prompts for **prompts2shorts**, ensuring your AI generates scripts, image queries, and voice styles exactly the way you want.

---

## 1. What is a System Prompt?

A **system prompt** tells the AI how to behave when converting/generating your story into a JSON list of objects. Each object must include three keys:

* `content`: the script text to be spoken in the video.
* `ai_image_query`: a concise, vivid scene description for image generation.
* `voice_style`: instructions for how the AI voice should read the content.

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
- voice_style: a description on how the ai voice should read the content and words or sentences in it.

Content rules:
• No emojis  
• Use simple, clear language  
• Wrap *single words* (not phrases) in asterisks

Image query rules:
• Be concise but detailed  
• Specify style (e.g. cinematic, watercolor)  
• Specify mood (e.g. eerie, joyful)  
• Specify composition (e.g. close-up, wide-angle)  
• Specify lighting (e.g. golden hour, backlit)  
• Use a simple color palette (e.g. muted earth tones)

Voice style rules:
• Must match the overall tone of the entire script
• Add emphasis to important words/sentences (e.g 'Louder for 'This is important')
• Note that the TTS Ai is not aware of the context of what its reading or the context of the content

Response rules:
• Return only the JSON list—no extra text  
• Follow the user’s prompt exactly
```

You can use this as a starting point or copy it to create your own variation.

---

## 3. Creating Your Own Prompt

1. **Copy** `base.txt` and rename it (e.g. `dramatic_narrator.txt`).
2. **Edit** the content to customize:

   * Add or refine **voice\_style rules** (e.g. "use a whisper during suspenseful lines").
   * Tweak **content rules** (e.g. "avoid superlatives").
   * Modify **image query rules** (e.g. "focus on pastel color schemes").
3. **Ensure** you still instruct the AI to output a JSON list of objects with exactly `content`, `ai_image_query`, and `voice_style` keys.

**Example snippet**:

```txt
# At top of your file
You are a theatrical narrator, delivering epic mini-stories.
Your output MUST be a JSON array of objects, each with keys: content, ai_image_query, voice_style.

Voice style rules:
• Speak with dramatic pauses—double pause after each sentence.
• Use a deep, resonant tone.

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

* **Be explicit**: The more detail you give in voice style (tone, pace, emotion), the more consistent your results.
* **Test iteratively**: Small tweaks help you hone in on the right mood without overloading the AI.
* **Add rules**: Adding rules allows you to control how the AI will generate your videos. Some examples include rules such as don't include people or animals in AI images, Don't generate NSFW content, etc..
* **Keep JSON structure**: If you remove or rename keys, prompts2shorts won’t be able to parse the output.
---