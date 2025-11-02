#!/bin/bash
# run_services.sh

# Start services with uv run and save their PIDs
uv run create_docs_database.py
uv run telegram_bot_rag.py &
TELEGRAM_PID=$!
uv run discord_bot_rag.py &
DISCORD_PID=$!
python commands.py &
COMMANDS_PID=$!

echo "Telegram bot running with PID $TELEGRAM_PID"
echo "Discord bot running with PID $DISCORD_PID"
echo "Commands bot running with PID $COMMANDS_PID"

# Trap CTRL+C to kill child processes
trap "echo 'Stopping services...'; kill $TELEGRAM_PID $DISCORD_PID $COMMANDS_PID" SIGINT

# Keep script running until killed
wait