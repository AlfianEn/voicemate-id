# VoiceMate ID

Indonesian voice-first AI assistant on Telegram. Send a voice note in Bahasa Indonesia, get a thoughtful spoken reply back. Fully voice-in, voice-out.

Built on **Xiaomi MiMo**:
- `mimo-reasoning` — handles understanding and answering
- `mimo-v2.5-tts` — speaks the reply back in natural Indonesian

## Why this exists

Indonesian users mostly *talk* with their phones, not type. Most AI assistants are text-first or English-first. VoiceMate ID flips that: open Telegram, hold record, talk in Bahasa Indonesia, get a spoken answer back in seconds.

It is a small showcase of what Xiaomi MiMo's reasoning + TTS stack can do when wired together for a real, daily use case.

## Features

- 🎙️ **Voice in** — send any Telegram voice note in Bahasa Indonesia
- 🧠 **Reasoning** — answers powered by `mimo-reasoning` with conversation memory
- 🔊 **Voice out** — replies sent back as voice notes via `mimo-v2.5-tts`
- 💬 **Text fallback** — replies also sent as text so you can read along
- 🇮🇩 **Indonesia-native** — prompts, persona, voices tuned for BI
- 🪶 **Lightweight** — single Python service, no extra infrastructure

## Stack

- Python 3.11+
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) — Telegram bot framework
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text) — speech-to-text (configurable)
- [Xiaomi MiMo Open Platform](https://platform.xiaomimimo.com/) — reasoning + TTS

## Quick start

### 1. Install

Requires [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/AlfianEn/voicemate-id.git
cd voicemate-id
uv sync
```

### 2. Configure

```bash
cp .env.example .env
```

Fill in:

- `TELEGRAM_BOT_TOKEN` — from [@BotFather](https://t.me/BotFather)
- `MIMO_API_KEY` — from [Xiaomi MiMo Platform](https://platform.xiaomimimo.com/)
- `OPENAI_API_KEY` — for Whisper STT (or swap to a local model later)

### 3. Run

```bash
uv run voicemate-bot
```

Talk to your bot on Telegram with a voice note.

## Project layout

```
voicemate-id/
├── src/voicemate/
│   ├── __init__.py
│   ├── __main__.py        # entry point
│   ├── config.py          # env-based settings
│   ├── bot.py             # Telegram handlers
│   ├── stt.py             # speech-to-text
│   ├── llm.py             # MiMo reasoning client
│   ├── tts.py             # MiMo TTS client
│   └── memory.py          # per-user short-term memory
├── tests/
├── .env.example
├── pyproject.toml
└── README.md
```

## Roadmap

- [x] Repo skeleton
- [ ] Telegram voice in/out flow
- [ ] MiMo reasoning integration
- [ ] MiMo TTS integration
- [ ] Per-user conversation memory
- [ ] Demo video
- [ ] Deploy guide (systemd unit + Docker)
- [ ] WhatsApp adapter (stretch)

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

Built for the [Xiaomi MiMo Orbit 100T Token Plan](https://100t.xiaomimimo.com/) creator program.
