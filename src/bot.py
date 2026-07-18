import logging
import os

import discord

from . import analysis, config, meme, topic

logger = logging.getLogger("meme_bot")


class MemeBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.failed = False

    async def on_ready(self):
        logger.info("Logged in as %s", self.user)
        try:
            await self.post_daily_meme()
        except Exception:
            logger.exception("Failed to post daily meme")
            self.failed = True
        finally:
            await self.close()

    async def post_daily_meme(self):
        channels_context = await self._collect_channel_context()
        humour_style, topics = analysis.analyze(channels_context)
        example_captions = analysis.top_examples(channels_context)
        logger.info("Humour style summary: %s", humour_style)
        logger.info("Generated topics: %s", topics)
        logger.info("Example captions: %s", example_captions)

        chosen_topic = topic.choose(topics)
        logger.info("Topic: %s", chosen_topic)

        image_url = meme.generate_meme(chosen_topic, humour_style, example_captions)
        logger.info("Generated meme: %s", image_url)

        post_channel = await self._get_channel(config.MEME_POST_CHANNEL_ID)
        await post_channel.send(content=f"Today's meme topic: **{chosen_topic}**\n{image_url}")

        _write_step_summary(humour_style, topics, example_captions, chosen_topic, image_url)

    async def _collect_channel_context(self) -> list[dict]:
        channels_context = []
        for channel_id in config.SOURCE_CHANNEL_IDS:
            channel = await self._get_channel(channel_id)
            messages = []
            async for message in channel.history(limit=config.MESSAGES_PER_CHANNEL_LIMIT):
                if message.author.bot:
                    continue
                text = message.content.strip()
                if message.attachments:
                    text = (text + " [image attached]").strip()
                if not text:
                    continue
                reactions = sum(r.count for r in message.reactions)
                messages.append({"text": text, "reactions": reactions})
            channels_context.append(
                {
                    "name": getattr(channel, "name", str(channel_id)),
                    "topic": getattr(channel, "topic", None) or "",
                    "messages": messages,
                }
            )
        return channels_context

    async def _get_channel(self, channel_id: int):
        return self.get_channel(channel_id) or await self.fetch_channel(channel_id)


def _write_step_summary(
    humour_style: str,
    topics: list[str],
    example_captions: list[str],
    chosen_topic: str,
    image_url: str,
):
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    topics_list = "\n".join(f"- {t}" for t in topics)
    examples_list = "\n".join(f"- {c}" for c in example_captions) or "(none)"
    with open(summary_path, "a") as f:
        f.write(
            f"## Daily meme\n\n"
            f"**Topic:** {chosen_topic}\n\n"
            f"**Humour style summary:**\n{humour_style}\n\n"
            f"**Today's generated topics:**\n{topics_list}\n\n"
            f"**Top-reacted example messages used as style reference:**\n{examples_list}\n\n"
            f"**Image:** {image_url}\n"
        )


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    client = MemeBot(intents=intents)
    client.run(config.DISCORD_BOT_TOKEN)
    if client.failed:
        raise SystemExit(1)
