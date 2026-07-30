from . import llm_client

SYSTEM_PROMPT = (
    "You write a short, funny weekly recap of a friend group's Discord chat "
    "to post back into their server. Be warm, funny, and specific — "
    "reference actual running jokes and moments from the messages given. "
    "Write like a group chat member, not a corporate summary."
)

DEFAULT_RECAP = (
    "Not enough happened this week to recap — or everyone's been suspiciously "
    "quiet. \U0001f440"
)


def generate_recap(channels: list[dict]) -> str:
    if not any(c["messages"] for c in channels):
        return DEFAULT_RECAP

    sections = []
    for c in channels:
        header = f"### #{c['name']}"
        if c["topic"]:
            header += f" (channel description: {c['topic']})"
        body = (
            "\n".join(f"- {m['text']} (reactions: {m['reactions']})" for m in c["messages"])
            or "(no messages this week)"
        )
        sections.append(f"{header}\n{body}")
    joined = "\n\n".join(sections)

    prompt = (
        "Here are this past week's messages from a friend group's Discord "
        "channels:\n\n"
        f"{joined}\n\n"
        "Write a short, funny weekly recap — roughly 5-10 short bullet "
        "points or a couple of punchy short paragraphs — highlighting the "
        "best running jokes, funniest moments, and any recurring "
        "themes/roasts from this week, judging by what actually got "
        "posted and reacted to. Write it as a message to post directly "
        "into the channel: plain conversational text, maybe a bit of "
        "emoji, no markdown headers. Keep the whole thing under 1500 "
        "characters."
    )
    return llm_client.ask(SYSTEM_PROMPT, prompt, max_tokens=1200)
