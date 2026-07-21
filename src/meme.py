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


def generate_meme(
    topics: list[str], humour_style: str, example_captions: list[str]
) -> tuple[str, str, str, list[str]]:
    """Drafts one candidate meme per topic, judges them, and renders the
    winner. Returns (image_url, chosen_topic, explanation, candidate_summaries)."""
    templates = imgflip.get_templates()
    template_list = "\n".join(
        f"- id={t['id']}: {t['name']} (box_count={t['box_count']})" for t in templates
    )
    topics_list = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(topics))

    prompt = (
        f"Today's candidate topics (draft ONE meme per topic, same order):\n"
        f"{topics_list}\n\n"
        f"This group's sense of humour:\n{humour_style}\n\n"
        f"{_examples_block(example_captions)}"
        "For each topic, choose the best-fitting meme template from this "
        f"list (box_count is how many text fields it has):\n{template_list}\n\n"
        "Reply with ONLY a JSON object like "
        '{"candidates": [{"topic": "...", "template_id": "...", "texts": '
        '["...", "..."], "explanation": "..."}, ...]} with exactly '
        f"{len(topics)} candidates, one per topic listed above, in the same "
        'order. "texts" must have exactly as many entries as the chosen '
        "template's box_count, in order. Keep each text entry short (under "
        "60 characters) and funny, written in this group's voice. "
        '"explanation" is one short, dry sentence explaining the joke or '
        "reference, for someone who might not immediately get it."
    )
    raw = llm_client.ask(GENERATE_SYSTEM_PROMPT, prompt, max_tokens=2500)
    data = json.loads(llm_client.strip_code_fence(raw))
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError("LLM returned no meme candidates")

    templates_by_id = {str(t["id"]): t for t in templates}
    best_index = _pick_best_index(humour_style, candidates, templates_by_id)
    best = candidates[best_index]

    candidate_summaries = [
        _format_candidate(i, c, templates_by_id, is_winner=(i == best_index))
        for i, c in enumerate(candidates)
    ]

    image_url = imgflip.caption_image(
        template_id=str(best["template_id"]),
        texts=best.get("texts") or [],
        username=config.IMGFLIP_USERNAME,
        password=config.IMGFLIP_PASSWORD,
    )
    return (
        image_url,
        best.get("topic") or topics[0],
        best.get("explanation") or "",
        candidate_summaries,
    )


def _pick_best_index(humour_style: str, candidates: list[dict], templates_by_id: dict) -> int:
    if len(candidates) == 1:
        return 0

    listing = "\n".join(
        _format_candidate(i, c, templates_by_id) for i, c in enumerate(candidates)
    )
    prompt = (
        f"This group's sense of humour:\n{humour_style}\n\n"
        f"Here are {len(candidates)} candidate memes drafted for today, "
        f"each on a different topic:\n{listing}\n\n"
        "Pick the funniest, best-fitting one for this specific group. "
        'Reply with ONLY a JSON object like {"best_index": 0}.'
    )
    raw = llm_client.ask(JUDGE_SYSTEM_PROMPT, prompt, max_tokens=500)
    data = json.loads(llm_client.strip_code_fence(raw))
    index = data.get("best_index", 0)
    if not isinstance(index, int) or not (0 <= index < len(candidates)):
        index = 0
    return index


def _format_candidate(
    i: int, c: dict, templates_by_id: dict, is_winner: bool = False
) -> str:
    template = templates_by_id.get(str(c.get("template_id")))
    template_name = template["name"] if template else c.get("template_id")
    texts = " / ".join(c.get("texts") or [])
    explanation = c.get("explanation") or ""
    marker = " (chosen)" if is_winner else ""
    return f'{i}: topic="{c.get("topic")}" [{template_name}] {texts} — {explanation}{marker}'


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
