from anthropic import Anthropic

from . import config

_client = Anthropic(api_key=config.ANTHROPIC_API_KEY)


def ask(system: str, prompt: str, max_tokens: int = 500) -> str:
    response = _client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()
