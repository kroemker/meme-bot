import os

from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
MEME_POST_CHANNEL_ID = int(os.environ["MEME_POST_CHANNEL_ID"])
SOURCE_CHANNEL_IDS = [
    int(channel_id) for channel_id in os.environ["SOURCE_CHANNEL_IDS"].split(",") if channel_id
]
IMGFLIP_USERNAME = os.environ["IMGFLIP_USERNAME"]
IMGFLIP_PASSWORD = os.environ["IMGFLIP_PASSWORD"]

HUMOUR_LOOKBACK_DAYS = int(os.environ.get("HUMOUR_LOOKBACK_DAYS", "7"))
MESSAGES_PER_CHANNEL_LIMIT = int(os.environ.get("MESSAGES_PER_CHANNEL_LIMIT", "200"))

# LLM provider selection: "anthropic" (default) or "openai".
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic").lower()
if LLM_PROVIDER not in ("anthropic", "openai"):
    raise ValueError(
        f"Unsupported LLM_PROVIDER: {LLM_PROVIDER!r} (expected 'anthropic' or 'openai')"
    )

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

if LLM_PROVIDER == "anthropic" and not ANTHROPIC_API_KEY:
    raise RuntimeError("LLM_PROVIDER=anthropic requires ANTHROPIC_API_KEY to be set")
if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
    raise RuntimeError("LLM_PROVIDER=openai requires OPENAI_API_KEY to be set")
