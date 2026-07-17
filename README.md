# meme-bot

A Discord bot that scans your meme channel(s) to get a feel for your friend
group's humour, then posts one AI-captioned meme a day to a channel of its
own.

## How it works

Once a day (via a GitHub Actions cron job):

1. Connects to Discord and reads the last 50 messages (per channel) from the
   configured source channel(s) (your meme channel + any others you want it
   to learn from).
2. Sends that context to an LLM (Anthropic or OpenAI — your choice) to get a
   short summary of the group's sense of humour.
3. Picks a random topic.
4. Asks the LLM to pick a matching [Imgflip](https://imgflip.com) template
   and write a top/bottom caption for it, in the group's style.
5. Renders the meme via the Imgflip API and posts it to the target channel.

## Setup

### 1. Create the Discord bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application.
2. Under **Bot**, create a bot user and copy its token — this is `DISCORD_BOT_TOKEN`.
3. Under **Bot**, enable the **Message Content Intent** (privileged intent) — the bot needs it to read message text.
4. Under **OAuth2 > URL Generator**, select the `bot` scope and these permissions: `View Channels`, `Read Message History`, `Send Messages`. Use the generated URL to invite the bot to your server.
5. Get the channel IDs (enable Developer Mode in Discord, then right-click a channel > Copy Channel ID):
   - `MEME_POST_CHANNEL_ID`: the channel the bot posts its daily meme to.
   - `SOURCE_CHANNEL_IDS`: comma-separated list of channel(s) it reads for humour context (your meme channel, and any others).

### 2. Get an LLM API key

Pick one provider (you can switch later via `LLM_PROVIDER`):

- **Anthropic** (default): create a key at [console.anthropic.com](https://console.anthropic.com) — this is `ANTHROPIC_API_KEY`. Note this is separate from a Claude Pro/Max subscription — Pro doesn't grant API access, the API is billed separately (pay-as-you-go, prepaid credit).
- **OpenAI**: create a key at [platform.openai.com](https://platform.openai.com/api-keys) — this is `OPENAI_API_KEY`. Same story — a ChatGPT Plus subscription doesn't grant API access, the API is billed separately.

Either way, cost for this bot is tiny — two short calls a day.

### 3. Get Imgflip credentials

Create a free account at [imgflip.com](https://imgflip.com) — `IMGFLIP_USERNAME` / `IMGFLIP_PASSWORD` are your account login.

### 4. Configure secrets

**For GitHub Actions (production):** in the repo, go to Settings > Secrets and variables > Actions, and add each of the variables below as a repository secret.

**For local testing:** copy `.env.example` to `.env` and fill in the same values.

| Variable | Description |
|---|---|
| `DISCORD_BOT_TOKEN` | Bot token from the Developer Portal |
| `MEME_POST_CHANNEL_ID` | Channel ID the bot posts to |
| `SOURCE_CHANNEL_IDS` | Comma-separated channel IDs the bot reads for humour context |
| `IMGFLIP_USERNAME` | Imgflip account username |
| `IMGFLIP_PASSWORD` | Imgflip account password |
| `LLM_PROVIDER` | Optional, default `anthropic` — set to `openai` to use OpenAI instead |
| `ANTHROPIC_API_KEY` | Required if `LLM_PROVIDER=anthropic` |
| `CLAUDE_MODEL` | Optional, default `claude-sonnet-5` |
| `OPENAI_API_KEY` | Required if `LLM_PROVIDER=openai` |
| `OPENAI_MODEL` | Optional, default `gpt-4o-mini` |
| `MESSAGES_PER_CHANNEL_LIMIT` | Optional, default `50` — max messages fetched per source channel |

Only the key pair for your chosen `LLM_PROVIDER` is required — you don't need
both, but you can set both and flip `LLM_PROVIDER` any time to switch.

### 5. Run it

Locally:

```bash
pip install -r requirements.txt
python main.py
```

In production, the `.github/workflows/daily-meme.yml` workflow runs this
automatically once a day (`0 18 * * *` UTC by default — edit the cron
expression to change the time). You can also trigger it manually from the
Actions tab via `workflow_dispatch`.

### Seeing what the LLM generated

Each run writes a summary — the humour style it inferred, the chosen topic,
and the resulting image URL — to the **Summary** panel of that Actions run
(Actions tab > pick the run). It's also in the raw job log if you want more
detail (e.g. `INFO:meme_bot:Humour style summary: ...`).

## Project layout

```
main.py              entrypoint
src/
  config.py           env var loading
  bot.py               Discord client: fetches history, posts the meme
  llm_client.py         Anthropic/OpenAI dispatcher (LLM_PROVIDER)
  humour.py            summarizes the group's humour via the LLM
  topic.py             random daily topic picker
  meme.py               picks a template + writes captions via the LLM
  imgflip.py           Imgflip API client
```
