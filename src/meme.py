import json

from . import claude_client, config, imgflip

SYSTEM_PROMPT = (
    "You write short, punchy meme captions in the style of a specific meme "
    "template. You always reply with strict JSON and nothing else."
)


def generate_meme(topic: str, humour_style: str) -> str:
    templates = imgflip.get_templates()
    template_list = "\n".join(f"- id={t['id']}: {t['name']}" for t in templates)

    prompt = (
        f"Topic for today's meme: {topic}\n\n"
        f"This group's sense of humour:\n{humour_style}\n\n"
        f"Choose the best-fitting meme template from this list:\n{template_list}\n\n"
        'Reply with ONLY a JSON object like {"template_id": "...", "top_text": '
        '"...", "bottom_text": "..."}. Keep each text line short (under 60 '
        "characters) and funny."
    )
    raw = claude_client.ask(SYSTEM_PROMPT, prompt, max_tokens=200)
    choice = json.loads(_strip_code_fence(raw))

    return imgflip.caption_image(
        template_id=str(choice["template_id"]),
        top_text=choice.get("top_text", ""),
        bottom_text=choice.get("bottom_text", ""),
        username=config.IMGFLIP_USERNAME,
        password=config.IMGFLIP_PASSWORD,
    )


def _strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[len("json") :]
    return text.strip()
