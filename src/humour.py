from . import llm_client

SYSTEM_PROMPT = (
    "You are analyzing recent messages from a Discord meme channel to summarize "
    "the group's sense of humour for someone about to write a new meme caption in "
    "their style. Be concise and concrete."
)

DEFAULT_STYLE = "No recent messages available; default to absurdist, dry internet humour."


def summarize(messages: list[str]) -> str:
    if not messages:
        return DEFAULT_STYLE

    joined = "\n".join(f"- {m}" for m in messages[:300])
    prompt = (
        "Here are recent messages (with reaction counts noted) from a friend "
        "group's meme channels:\n\n"
        f"{joined}\n\n"
        "In 3-5 bullet points, describe this group's sense of humour: recurring "
        "themes, tone (dry/absurd/wholesome/dark/etc.), running jokes, and what "
        "kind of captions tend to land well."
    )
    return llm_client.ask(SYSTEM_PROMPT, prompt, max_tokens=300)
