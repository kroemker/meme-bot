# meme-bot

A Discord bot that scans your meme channel(s) to get a feel for your friend
group's humour, then posts one AI-captioned meme a day and a weekly recap to
a channel of its own.

## How it works

### Daily meme (via a GitHub Actions cron job)

1. Connects to Discord and reads the last 100 messages (per channel), plus
   each channel's name and description, from the configured source
   channel(s) (your meme channel + any others you want it to learn from).
   Links in messages (YouTube especially, plus a best-effort page-title
   fetch for other links) are resolved to a short description — e.g. a bare
   `https://youtu.be/...` becomes `[YouTube: "title" by channel]` — so the
   LLM understands link-only posts instead of seeing an opaque URL.
2. Sends all of that to an LLM (Anthropic or OpenAI — your choice) in one
   call to get both a summary of the group's sense of humour and a list of
   10 fresh topic ideas grounded in what the group actually talks about.
   Topics are allowed to recur — a small friend group only has so many
   genuinely distinct running themes, so repeating a topic (a game, a
   recurring bit) from a fresh angle is fine and expected.
3. Randomly samples 3 of those 10 topics.
4. Scans the bot's own recent posts in the target channel for the last 10
   joke explanations it's already used (parsed straight out of its own past
   messages' spoiler text, no separate state to maintain), then asks the
   LLM to draft one candidate meme per sampled topic — each free to pick
   its own best-fitting template from up to 100
   [Imgflip](https://imgflip.com) templates (any box count, not just
   top/bottom) — using the group's most-reacted recent messages as concrete
   style examples, and explicitly avoiding those last 10 joke angles/
   premises even if the topic overlaps. Topic and template are chosen
   together per candidate, rather than picking a topic first and fitting a
   template to it after.
5. A second LLM call judges the 3 drafts and picks the funniest, best-fitting
   one for the group.
6. Renders the winning meme via the Imgflip API and posts it to the target
   channel, with a one-line explanation of the joke posted underneath as a
   Discord spoiler (`||like this||`) for anyone who doesn't get it.

Nothing is persisted between days — the recent-jokes check is derived by
reading the channel's own message history each run, not stored anywhere
separately. Topics themselves are unrestricted; only the specific joke/
punchline is required to be fresh each time.

### Weekly recap (via a second GitHub Actions cron job)

Once a week, the bot reads the past 7 days of messages (time-windowed, not
capped by message count like the daily job) from the same source channels
and asks the LLM to write a short, funny recap of the week's running jokes
and highlights, posted as plain text to the same target channel — no image
generation involved.

## Setup

### 1. Create the Discord bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application.
2. Under **Bot**, create a bot user and copy its token — this is `DISCORD_BOT_TOKEN`.
3. Under **Bot**, enable the **Message Content Intent** (privileged intent) — the bot needs it to read message text.
4. Under **OAuth2 > URL Generator**, select the `bot` scope and these permissions: `View Channels`, `Read Message History`, `Send Messages`. Use the generated URL to invite the bot to your server.
5. Get the channel IDs (enable Developer Mode in Discord, then right-click a channel > Copy Channel ID):
   - `MEME_POST_CHANNEL_ID`: the channel the bot posts its daily meme to.
   - `SOURCE_CHANNEL_IDS`: comma-separated list of channel(s) it reads for humour context (your meme channel, and any others).
6. Optional but recommended: set a **channel topic/description** on your meme channel (Edit Channel > Topic) — e.g. "post your best/worst memes, we roast each other." The bot reads this alongside the channel name so the LLM knows what the channel is actually for instead of guessing.

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
| `OPENAI_MODEL` | Optional, default `gpt-5.6-terra` |
| `MESSAGES_PER_CHANNEL_LIMIT` | Optional, default `100` — max messages fetched per source channel for the daily meme |
| `RUN_MODE` | Optional, default `daily_meme` — set to `weekly_recap` by the weekly workflow, not something you need to set yourself |
| `RECAP_LOOKBACK_DAYS` | Optional, default `7` — how many days back the weekly recap looks |
| `RECAP_MESSAGES_PER_CHANNEL_LIMIT` | Optional, default `500` — safety cap on messages fetched per channel for the recap |

Only the key pair for your chosen `LLM_PROVIDER` is required — you don't need
both, but you can set both and flip `LLM_PROVIDER` any time to switch.

### 5. Run it

Locally:

```bash
pip install -r requirements.txt
python main.py
```

In production, two workflows run this automatically:

- `.github/workflows/daily-meme.yml` — daily (`0 18 * * *` UTC by default).
- `.github/workflows/weekly-recap.yml` — weekly, Sundays (`0 18 * * 0` UTC by
  default), sets `RUN_MODE=weekly_recap`.

Edit the cron expressions to change the timing. Both can also be triggered
manually from the Actions tab via `workflow_dispatch`.

### Seeing what the LLM generated

Each daily-meme run writes a summary — the inferred humour style, the 10
generated topics, the last-10 joke angles it was told to avoid, the 3
candidate memes drafted (topic, template, texts, explanation, and which one
won), the top-reacted messages used as style examples, and the resulting
image URL — to the **Summary** panel of that Actions run (Actions tab > pick
the run).
Each weekly-recap run writes the generated recap text there too. It's also
in the raw job log if you want more detail (e.g.
`INFO:meme_bot:Humour style summary: ...`).

## Project layout

```
main.py              entrypoint
src/
  config.py           env var loading
  bot.py               Discord client: fetches history, posts the meme/recap
  llm_client.py         Anthropic/OpenAI dispatcher (LLM_PROVIDER)
  analysis.py           humour-style summary + topic ideas, one LLM call
  topic.py             random sample from the generated topics
  meme.py               drafts candidates, judges, writes captions via the LLM
  imgflip.py           Imgflip API client
  links.py             resolves URLs in messages to short descriptions
  recap.py             weekly recap text generation via the LLM
```
