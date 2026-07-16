import datetime
import logging

import discord

from . import config, humour, meme, topic

logger = logging.getLogger("meme_bot")


class MemeBot(discord.Client):
    async def on_ready(self):
        logger.info("Logged in as %s", self.user)
        try:
            await self.post_daily_meme()
        except Exception:
            logger.exception("Failed to post daily meme")
        finally:
            await self.close()

    async def post_daily_meme(self):
        recent_messages = await self._collect_recent_messages()
        humour_style = humour.summarize(recent_messages)
        logger.info("Humour style summary: %s", humour_style)

        chosen_topic = topic.random_topic()
        logger.info("Topic: %s", chosen_topic)

        image_url = meme.generate_meme(chosen_topic, humour_style)
        logger.info("Generated meme: %s", image_url)

        post_channel = await self._get_channel(config.MEME_POST_CHANNEL_ID)
        await post_channel.send(content=f"Today's meme topic: **{chosen_topic}**\n{image_url}")

    async def _collect_recent_messages(self) -> list[str]:
        cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
            days=config.HUMOUR_LOOKBACK_DAYS
        )
        collected = []
        for channel_id in config.SOURCE_CHANNEL_IDS:
            channel = await self._get_channel(channel_id)
            async for message in channel.history(
                limit=config.MESSAGES_PER_CHANNEL_LIMIT, after=cutoff
            ):
                if message.author.bot:
                    continue
                text = message.content.strip()
                if message.attachments:
                    text = (text + " [image attached]").strip()
                if not text:
                    continue
                reactions = sum(r.count for r in message.reactions)
                collected.append(f"{text} (reactions: {reactions})")
        return collected

    async def _get_channel(self, channel_id: int):
        return self.get_channel(channel_id) or await self.fetch_channel(channel_id)


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    client = MemeBot(intents=intents)
    client.run(config.DISCORD_BOT_TOKEN)
