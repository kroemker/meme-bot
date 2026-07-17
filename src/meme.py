import json

from . import config, imgflip, llm_client

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
    raw = llm_client.ask(SYSTEM_PROMPT, prompt, max_tokens=800)
    choice = json.loads(llm_client.strip_code_fence(raw))

    return imgflip.caption_image(
        template_id=str(choice["template_id"]),
        top_text=choice.get("top_text", ""),
        bottom_text=choice.get("bottom_text", ""),
        username=config.IMGFLIP_USERNAME,
        password=config.IMGFLIP_PASSWORD,
    )
