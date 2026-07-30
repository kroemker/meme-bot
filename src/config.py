import os

from dotenv import load_dotenv

load_dotenv()


def _env(key: str, default: str) -> str:
    # GitHub Actions sets referenced secrets as an empty-string env var even
    # when the secret doesn't exist, so a plain os.environ.get(key, default)
    # would never fall back to the default in that case.
    return os.environ.get(key) or default


DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
MEME_POST_CHANNEL_ID = int(os.environ["MEME_POST_CHANNEL_ID"])
SOURCE_CHANNEL_IDS = [
    int(channel_id) for channel_id in os.environ["SOURCE_CHANNEL_IDS"].split(",") if channel_id
]
IMGFLIP_USERNAME = os.environ["IMGFLIP_USERNAME"]
IMGFLIP_PASSWORD = os.environ["IMGFLIP_PASSWORD"]

MESSAGES_PER_CHANNEL_LIMIT = int(_env("MESSAGES_PER_CHANNEL_LIMIT", "100"))

# "daily_meme" (default) or "weekly_recap".
RUN_MODE = _env("RUN_MODE", "daily_meme")
if RUN_MODE not in ("daily_meme", "weekly_recap"):
    raise ValueError(
        f"Unsupported RUN_MODE: {RUN_MODE!r} (expected 'daily_meme' or 'weekly_recap')"
    )

RECAP_LOOKBACK_DAYS = int(_env("RECAP_LOOKBACK_DAYS", "7"))
RECAP_MESSAGES_PER_CHANNEL_LIMIT = int(_env("RECAP_MESSAGES_PER_CHANNEL_LIMIT", "500"))

# LLM provider selection: "anthropic" (default) or "openai".
LLM_PROVIDER = _env("LLM_PROVIDER", "anthropic").lower()
if LLM_PROVIDER not in ("anthropic", "openai"):
    raise ValueError(
        f"Unsupported LLM_PROVIDER: {LLM_PROVIDER!r} (expected 'anthropic' or 'openai')"
    )

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = _env("CLAUDE_MODEL", "claude-sonnet-5")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = _env("OPENAI_MODEL", "gpt-5.6-terra")

if LLM_PROVIDER == "anthropic" and not ANTHROPIC_API_KEY:
    raise RuntimeError("LLM_PROVIDER=anthropic requires ANTHROPIC_API_KEY to be set")
if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
    raise RuntimeError("LLM_PROVIDER=openai requires OPENAI_API_KEY to be set")
