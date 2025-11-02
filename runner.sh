#!/bin/bash
# run_services.sh

echo "🔄 Building documentation database..."
# Build the database first (runs synchronously)
uv run create_docs_database.py

echo ""
echo "🚀 Starting bot services..."
# Start bot services in background and save their PIDs
uv run telegram_bot_rag.py &
TELEGRAM_PID=$!

uv run discord_bot_rag.py &
DISCORD_PID=$!

echo ""
echo "✅ Services started:"
echo "   📱 Telegram bot (RAG + Commands) - PID $TELEGRAM_PID"
echo "   💬 Discord bot (RAG) - PID $DISCORD_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Trap CTRL+C to kill child processes
trap "echo '\n⏹️  Stopping services...'; kill $TELEGRAM_PID $DISCORD_PID 2>/dev/null; echo '✅ All services stopped'; exit 0" SIGINT SIGTERM

# Keep script running until killed
wait