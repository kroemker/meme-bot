from . import config

_anthropic_client = None
_openai_client = None


def ask(system: str, prompt: str, max_tokens: int = 500) -> str:
    if config.LLM_PROVIDER == "openai":
        return _ask_openai(system, prompt, max_tokens)
    return _ask_anthropic(system, prompt, max_tokens)


def _ask_anthropic(system: str, prompt: str, max_tokens: int) -> str:
    global _anthropic_client
    if _anthropic_client is None:
        from anthropic import Anthropic

        _anthropic_client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    response = _anthropic_client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def _ask_openai(system: str, prompt: str, max_tokens: int) -> str:
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI

        _openai_client = OpenAI(api_key=config.OPENAI_API_KEY)

    response = _openai_client.chat.completions.create(
        model=config.OPENAI_MODEL,
        max_completion_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    choice = response.choices[0]
    content = (choice.message.content or "").strip()
    if not content:
        raise RuntimeError(
            f"OpenAI returned no content (finish_reason={choice.finish_reason!r}). "
            "Reasoning models can consume the whole max_completion_tokens budget "
            "on hidden reasoning before writing any visible output — try raising "
            "max_tokens for this call."
        )
    return content


def strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[len("json") :]
    return text.strip()
