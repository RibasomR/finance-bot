<h1 align="center">💰 Finance Bot — Personal Finance Tracker for Telegram</h1>

<p align="center">
  <strong>Track expenses with voice messages. Just say it — the bot gets it.</strong><br>
  AI parses your voice into structured transactions. Supports any OpenAI-compatible provider.
</p>

<p align="center">
  <a href="#how-it-works">How It Works</a> •
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#configuration">Configuration</a> •
  <a href="#license">License</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white&style=for-the-badge" alt="Python">
  <img src="https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram&logoColor=white&style=for-the-badge" alt="Telegram">
  <img src="https://img.shields.io/badge/AI-OpenAI--Compatible-purple?logo=openai&logoColor=white&style=for-the-badge" alt="AI">
  <img src="https://img.shields.io/badge/Docker-Ready-blue?logo=docker&logoColor=white&style=for-the-badge" alt="Docker">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License">
</p>

---

You spend money every day but never know where it goes. Opening a banking app, scrolling through transactions, trying to categorize them manually — nobody does that for more than a week. **Finance Bot takes a different approach**: you just talk.

_"Spent 500 on groceries"_ — send a voice message to the bot in Telegram. AI transcribes it, parses the amount, guesses the category, and saves the transaction. That's it. At the end of the month, you ask for stats and see where your money went. No spreadsheets, no manual input — just natural conversation.

## How It Works

```
🎤 You: [voice message] "Got paid 3000 dollars for freelance"

🤖 Bot:
   ✅ Transaction saved!
   💰 Type: Income
   💵 Amount: $3,000
   🏷️ Category: Freelance

📊 You: /stats
🤖 Bot: This month — Income: $3,000 | Expenses: $1,240 | Balance: +$1,760
```

Send a voice message or type it out — the bot understands both. It figures out the type (income or expense), amount, currency, and category automatically.

## Features

- **Voice input** — send a voice message, Whisper transcribes it, LLM parses the transaction
- **Text input** — prefer typing? Works the same way
- **Smart categories** — AI assigns categories automatically, or you pick your own
- **Multi-currency** — RUB and USD out of the box
- **Statistics** — daily, weekly, monthly breakdowns with category splits
- **Excel export** — download your transactions as `.xlsx`
- **Custom categories** — create, rename, delete your own categories
- **Rate limiting** — Redis-based protection against spam
- **Any AI provider** — Groq, OpenAI, Ollama, or any OpenAI-compatible API

## Quick Start

### With Docker (recommended)

```bash
git clone https://github.com/RibasomR/finance-bot.git
cd finance-bot
cp .env.example .env
nano .env  # Fill in BOT_TOKEN and AI_API_KEY
docker compose up -d
```

> **Upgrading?** If you're updating from a previous version, run migrations:
> ```bash
> docker compose exec bot alembic upgrade head
> ```

### Without Docker

```bash
git clone https://github.com/RibasomR/finance-bot.git
cd finance-bot
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # Fill in BOT_TOKEN and AI_API_KEY
alembic upgrade head  # Run database migrations
python main.py
```

> SQLite is used by default for development. Switch `DATABASE_URL` to PostgreSQL for production.

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Launch the bot |
| `/menu` | Main menu |
| `/add` | Add a transaction |
| `/transactions` | View all transactions |
| `/stats` | Statistics |
| `/help` | Help |

## Configuration

All settings are in `.env`. The bot uses **any OpenAI-compatible API** — just point it to the right URL.

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | Yes | Telegram bot token from @BotFather |
| `AI_BASE_URL` | No | API endpoint (default: Groq) |
| `AI_API_KEY` | Yes | API key for your AI provider |
| `AI_CHAT_MODEL` | No | Model for text parsing (default: `llama-3.3-70b-versatile`) |
| `AI_WHISPER_MODEL` | No | Model for transcription (default: `whisper-large-v3-turbo`) |
| `AI_PROXY` | No | HTTP proxy for AI API requests |
| `DATABASE_URL` | Yes | Database connection string |
| `REDIS_URL` | No | Redis for rate limiting (falls back to in-memory) |

**Provider examples:**

```bash
# Groq (free tier available)
AI_BASE_URL=https://api.groq.com/openai/v1
AI_API_KEY=gsk_...

# OpenAI
AI_BASE_URL=https://api.openai.com/v1
AI_API_KEY=sk-...
AI_CHAT_MODEL=gpt-4o-mini
AI_WHISPER_MODEL=whisper-1

# Ollama (local)
AI_BASE_URL=http://localhost:11434/v1
AI_API_KEY=ollama
AI_CHAT_MODEL=llama3
```

## Project Structure

```
finance-bot/
├── bot/
│   ├── handlers/       # Command handlers (voice, transactions, stats...)
│   ├── keyboards/      # Inline & reply keyboards
│   ├── models/         # SQLAlchemy models (User, Transaction, Category)
│   ├── services/       # Business logic (AI, database, export)
│   ├── middlewares/     # Rate limiting, error handling
│   ├── states/         # FSM states for multi-step flows
│   └── utils/          # Logging, validation, sanitization
├── alembic/            # Database migrations
├── config/             # Pydantic Settings configuration
├── docker-compose.yml  # PostgreSQL + Redis + Bot
├── Dockerfile
├── main.py             # Entry point
└── requirements.txt
```

## Tech Stack

- **aiogram 3.x** — async Telegram Bot framework
- **SQLAlchemy 2.0** + **Alembic** — async ORM + migrations
- **Pydantic Settings** — configuration management
- **httpx** — async HTTP client for AI API
- **Redis** — rate limiting (optional, falls back to in-memory)
- **Docker Compose** — one-command deployment

## License

[MIT](LICENSE) — do whatever you want.
