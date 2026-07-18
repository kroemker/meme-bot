import json

from . import config, imgflip, llm_client

SYSTEM_PROMPT = (
    "You write short, punchy meme captions in the style of a specific meme "
    "template. You always reply with strict JSON and nothing else."
)


def generate_meme(topic: str, humour_style: str, example_captions: list[str]) -> str:
    templates = imgflip.get_templates()
    template_list = "\n".join(
        f"- id={t['id']}: {t['name']} (box_count={t['box_count']})" for t in templates
    )

    examples_block = ""
    if example_captions:
        examples = "\n".join(f"- {c}" for c in example_captions)
        examples_block = (
            "Here are some of this group's actual messages that got the most "
            "reactions in their meme channel(s) — use these as concrete "
            "examples of their tone, phrasing, and sense of humour (don't "
            "just copy them):\n"
            f"{examples}\n\n"
        )

    prompt = (
        f"Topic for today's meme: {topic}\n\n"
        f"This group's sense of humour:\n{humour_style}\n\n"
        f"{examples_block}"
        "Choose the best-fitting meme template from this list (box_count is "
        f"how many text fields it has):\n{template_list}\n\n"
        'Reply with ONLY a JSON object like {"template_id": "...", "texts": '
        '["...", "..."]}. The "texts" array must have exactly as many '
        "entries as the chosen template's box_count, in order. Keep each "
        "entry short (under 60 characters) and funny, written in this "
        "group's voice."
    )
    raw = llm_client.ask(SYSTEM_PROMPT, prompt, max_tokens=800)
    choice = json.loads(llm_client.strip_code_fence(raw))

    return imgflip.caption_image(
        template_id=str(choice["template_id"]),
        texts=choice.get("texts") or [],
        username=config.IMGFLIP_USERNAME,
        password=config.IMGFLIP_PASSWORD,
    )
