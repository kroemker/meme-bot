import os

from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
MEME_POST_CHANNEL_ID = int(os.environ["MEME_POST_CHANNEL_ID"])
SOURCE_CHANNEL_IDS = [
    int(channel_id) for channel_id in os.environ["SOURCE_CHANNEL_IDS"].split(",") if channel_id
]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
IMGFLIP_USERNAME = os.environ["IMGFLIP_USERNAME"]
IMGFLIP_PASSWORD = os.environ["IMGFLIP_PASSWORD"]

HUMOUR_LOOKBACK_DAYS = int(os.environ.get("HUMOUR_LOOKBACK_DAYS", "7"))
MESSAGES_PER_CHANNEL_LIMIT = int(os.environ.get("MESSAGES_PER_CHANNEL_LIMIT", "200"))
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")
