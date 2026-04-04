<h1 align="center">💰 Finance Bot — Учёт финансов в Telegram</h1>

<p align="center">
  <strong>Скажи боту, сколько потратил — он всё запишет.</strong><br>
  Голосовой ввод, AI-парсинг, статистика. Любой OpenAI-совместимый провайдер.
</p>

<p align="center">
  <a href="#как-это-работает">Как это работает</a> •
  <a href="#возможности">Возможности</a> •
  <a href="#быстрый-старт">Быстрый старт</a> •
  <a href="#настройка">Настройка</a> •
  <a href="#лицензия">Лицензия</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white&style=for-the-badge" alt="Python">
  <img src="https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram&logoColor=white&style=for-the-badge" alt="Telegram">
  <img src="https://img.shields.io/badge/AI-OpenAI--Compatible-purple?logo=openai&logoColor=white&style=for-the-badge" alt="AI">
  <img src="https://img.shields.io/badge/Docker-Ready-blue?logo=docker&logoColor=white&style=for-the-badge" alt="Docker">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License">
</p>

---

Каждый день ты тратишь деньги, но никогда толком не знаешь — куда. Открыть банковское приложение, листать историю, пытаться вручную раскидать по категориям — хватает максимум на неделю. **Finance Bot подходит к этому иначе**: ты просто говоришь.

_«Потратил 500 на продукты»_ — отправь голосовое сообщение боту в Telegram. AI расшифрует речь, вытащит сумму, угадает категорию и сохранит транзакцию. Всё. В конце месяца спрашиваешь статистику — и видишь, куда ушли деньги. Без таблиц, без ручного ввода — просто разговор.

## Как это работает

```
🎤 Ты: [голосовое] «Получил три тысячи долларов за фриланс»

🤖 Бот:
   ✅ Транзакция сохранена!
   💰 Тип: Доход
   💵 Сумма: $3,000
   🏷️ Категория: Фриланс

📊 Ты: /stats
🤖 Бот: Этот месяц — Доходы: $3,000 | Расходы: $1,240 | Баланс: +$1,760
```

Отправь голосовое или напиши текстом — бот понимает и то, и другое. Сам определит тип (доход или расход), сумму, валюту и категорию.

## Возможности

- **Голосовой ввод** — отправляешь войс, Whisper расшифровывает, LLM парсит транзакцию
- **Текстовый ввод** — предпочитаешь печатать? Работает так же
- **Умные категории** — AI сам назначает категорию, или выбираешь вручную
- **Мультивалютность** — рубли и доллары из коробки
- **Статистика** — разбивка по дням, неделям, месяцам с детализацией по категориям
- **Экспорт в Excel** — скачивай транзакции в `.xlsx`
- **Свои категории** — создавай, переименовывай, удаляй
- **Rate limiting** — защита от спама на базе Redis
- **Любой AI-провайдер** — Groq, OpenAI, Ollama или любой OpenAI-совместимый API

## Быстрый старт

### С Docker (рекомендуется)

```bash
git clone https://github.com/RibasomR/finance-bot.git
cd finance-bot
cp .env.example .env
nano .env  # Заполни BOT_TOKEN и AI_API_KEY
docker compose up -d
```

### Без Docker

```bash
git clone https://github.com/RibasomR/finance-bot.git
cd finance-bot
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # Заполни BOT_TOKEN и AI_API_KEY
python main.py
```

> По умолчанию используется SQLite для разработки. Для прода переключи `DATABASE_URL` на PostgreSQL.

## Команды

| Команда | Описание |
|---------|----------|
| `/start` | Запуск бота |
| `/menu` | Главное меню |
| `/add` | Добавить транзакцию |
| `/transactions` | Все транзакции |
| `/stats` | Статистика |
| `/help` | Справка |

## Настройка

Все параметры в `.env`. Бот работает с **любым OpenAI-совместимым API** — просто укажи нужный URL.

| Переменная | Обязательна | Описание |
|------------|-------------|----------|
| `BOT_TOKEN` | Да | Токен Telegram-бота от @BotFather |
| `AI_BASE_URL` | Нет | Эндпоинт API (по умолчанию: Groq) |
| `AI_API_KEY` | Да | API-ключ AI-провайдера |
| `AI_CHAT_MODEL` | Нет | Модель для парсинга текста (по умолчанию: `llama-3.3-70b-versatile`) |
| `AI_WHISPER_MODEL` | Нет | Модель для транскрипции (по умолчанию: `whisper-large-v3-turbo`) |
| `AI_PROXY` | Нет | HTTP-прокси для запросов к AI API |
| `DATABASE_URL` | Да | Строка подключения к БД |
| `REDIS_URL` | Нет | Redis для rate limiting (без него — in-memory) |

**Примеры провайдеров:**

```bash
# Groq (есть бесплатный тариф)
AI_BASE_URL=https://api.groq.com/openai/v1
AI_API_KEY=gsk_...

# OpenAI
AI_BASE_URL=https://api.openai.com/v1
AI_API_KEY=sk-...
AI_CHAT_MODEL=gpt-4o-mini
AI_WHISPER_MODEL=whisper-1

# Ollama (локально)
AI_BASE_URL=http://localhost:11434/v1
AI_API_KEY=ollama
AI_CHAT_MODEL=llama3
```

## Структура проекта

```
finance-bot/
├── bot/
│   ├── handlers/       # Обработчики команд (голос, транзакции, статистика...)
│   ├── keyboards/      # Inline и reply клавиатуры
│   ├── models/         # SQLAlchemy модели (User, Transaction, Category)
│   ├── services/       # Бизнес-логика (AI, база данных, экспорт)
│   ├── middlewares/    # Rate limiting, обработка ошибок
│   ├── states/         # FSM-состояния для многошаговых сценариев
│   └── utils/          # Логирование, валидация, санитизация
├── alembic/            # Миграции базы данных
├── config/             # Конфигурация (Pydantic Settings)
├── docker-compose.yml  # PostgreSQL + Redis + Bot
├── Dockerfile
├── main.py             # Точка входа
└── requirements.txt
```

## Стек

- **aiogram 3.x** — асинхронный Telegram Bot фреймворк
- **SQLAlchemy 2.0** + **Alembic** — async ORM + миграции
- **Pydantic Settings** — управление конфигурацией
- **httpx** — асинхронный HTTP-клиент для AI API
- **Redis** — rate limiting (опционально, фолбэк на in-memory)
- **Docker Compose** — деплой одной командой

## Лицензия

[MIT](LICENSE) — делай что хочешь.
