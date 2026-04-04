#!/bin/sh
## Entrypoint script for Finance Bot Docker container
## Handles migrations and starts the bot

set -e

echo "⏳ Waiting for services to be ready..."
sleep 5

echo "🔄 Running database migrations..."
if alembic upgrade head; then
    echo "✅ Migrations applied successfully"
else
    echo "❌ Migration failed"
    exit 1
fi

echo "🚀 Starting bot..."
exec python main.py

