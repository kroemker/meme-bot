import json

from . import llm_client

SYSTEM_PROMPT = (
    "You analyze a friend group's Discord channels to brief another AI that will "
    "generate a new meme in their style. Always reply with strict JSON and "
    "nothing else."
)

DEFAULT_HUMOUR_STYLE = "No recent messages available; default to absurdist, dry internet humour."
DEFAULT_TOPICS = [
    "Mondays",
    "coffee addiction",
    "procrastination",
    "the gym",
    "group chats",
    "adulting",
    "wifi issues",
    "online shopping",
    "sleep schedules",
    "AI taking over",
]


def analyze(channels: list[dict]) -> tuple[str, list[str]]:
    if not any(c["messages"] for c in channels):
        return DEFAULT_HUMOUR_STYLE, DEFAULT_TOPICS

    sections = []
    for c in channels:
        header = f"### #{c['name']}"
        if c["topic"]:
            header += f" (channel description: {c['topic']})"
        body = (
            "\n".join(f"- {m['text']} (reactions: {m['reactions']})" for m in c["messages"])
            or "(no recent messages)"
        )
        sections.append(f"{header}\n{body}")
    joined = "\n\n".join(sections)

    prompt = (
        "Here are recent messages from a friend group's Discord channels, "
        "including their meme channel(s) where they post memes for each other "
        "(each channel's name and description, if set, are given so you know "
        "what the channel is for):\n\n"
        f"{joined}\n\n"
        "Respond with ONLY a JSON object with two keys:\n"
        '- "humour_style": 3-5 bullet points (as a single newline-separated '
        "string) describing this group's sense of humour — recurring "
        "themes, tone (dry/absurd/wholesome/dark/etc.), running jokes, and "
        "what kind of captions tend to land well, judging by what actually "
        "gets posted and reacted to in their meme channel(s).\n"
        '- "topics": a list of exactly 20 short, varied topic phrases (2-5 '
        "words each) that would make for a funny meme for this specific "
        "group, inspired by what they actually talk about and joke about."
    )
    raw = llm_client.ask(SYSTEM_PROMPT, prompt, max_tokens=2000)
    data = json.loads(llm_client.strip_code_fence(raw))

    humour_style = data.get("humour_style") or DEFAULT_HUMOUR_STYLE
    topics = data.get("topics") or DEFAULT_TOPICS
    return humour_style, topics


def top_examples(channels: list[dict], limit: int = 8) -> list[str]:
    candidates = [
        m
        for c in channels
        for m in c["messages"]
        if m["text"] != "[image attached]"
    ]
    candidates.sort(key=lambda m: m["reactions"], reverse=True)
    return [m["text"] for m in candidates[:limit]]
