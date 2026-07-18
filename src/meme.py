import json

from . import config, imgflip, llm_client

GENERATE_SYSTEM_PROMPT = (
    "You write short, punchy meme captions in the style of a specific meme "
    "template. You always reply with strict JSON and nothing else."
)

JUDGE_SYSTEM_PROMPT = (
    "You are a discerning comedy critic judging meme drafts for a specific "
    "friend group. You always reply with strict JSON and nothing else."
)

CANDIDATE_COUNT = 3


def generate_meme(topic: str, humour_style: str, example_captions: list[str]) -> str:
    templates = imgflip.get_templates()
    template_list = "\n".join(
        f"- id={t['id']}: {t['name']} (box_count={t['box_count']})" for t in templates
    )

    prompt = (
        f"Topic for today's meme: {topic}\n\n"
        f"This group's sense of humour:\n{humour_style}\n\n"
        f"{_examples_block(example_captions)}"
        "Choose the best-fitting meme template from this list (box_count is "
        f"how many text fields it has):\n{template_list}\n\n"
        f"Generate {CANDIDATE_COUNT} DIFFERENT candidate memes — vary the "
        "template and/or the joke angle across candidates, don't just "
        "reword the same idea. Reply with ONLY a JSON object like "
        '{"candidates": [{"template_id": "...", "texts": ["...", "..."]}, '
        '...]}. Each candidate\'s "texts" array must have exactly as many '
        "entries as its chosen template's box_count, in order. Keep each "
        "entry short (under 60 characters) and funny, written in this "
        "group's voice."
    )
    raw = llm_client.ask(GENERATE_SYSTEM_PROMPT, prompt, max_tokens=2000)
    data = json.loads(llm_client.strip_code_fence(raw))
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError("LLM returned no meme candidates")

    templates_by_id = {str(t["id"]): t for t in templates}
    best = _pick_best(topic, humour_style, candidates, templates_by_id)

    return imgflip.caption_image(
        template_id=str(best["template_id"]),
        texts=best.get("texts") or [],
        username=config.IMGFLIP_USERNAME,
        password=config.IMGFLIP_PASSWORD,
    )


def _pick_best(
    topic: str, humour_style: str, candidates: list[dict], templates_by_id: dict
) -> dict:
    if len(candidates) == 1:
        return candidates[0]

    listing = []
    for i, c in enumerate(candidates):
        template = templates_by_id.get(str(c.get("template_id")))
        template_name = template["name"] if template else c.get("template_id")
        texts = " / ".join(c.get("texts") or [])
        listing.append(f"{i}: [{template_name}] {texts}")
    listing_block = "\n".join(listing)

    prompt = (
        f"Topic: {topic}\n\n"
        f"This group's sense of humour:\n{humour_style}\n\n"
        f"Here are {len(candidates)} candidate memes drafted for today:\n"
        f"{listing_block}\n\n"
        "Pick the funniest, best-fitting one for this specific group. "
        'Reply with ONLY a JSON object like {"best_index": 0}.'
    )
    raw = llm_client.ask(JUDGE_SYSTEM_PROMPT, prompt, max_tokens=500)
    data = json.loads(llm_client.strip_code_fence(raw))
    index = data.get("best_index", 0)
    if not isinstance(index, int) or not (0 <= index < len(candidates)):
        index = 0
    return candidates[index]


def _examples_block(example_captions: list[str]) -> str:
    if not example_captions:
        return ""
    examples = "\n".join(f"- {c}" for c in example_captions)
    return (
        "Here are some of this group's actual messages that got the most "
        "reactions in their meme channel(s) — use these as concrete "
        "examples of their tone, phrasing, and sense of humour (don't just "
        "copy them):\n"
        f"{examples}\n\n"
    )
