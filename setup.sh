#!/bin/bash

# RAG Bot Setup Script
echo "🚀 Setting up RAG Bot environment..."

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "📦 Creating virtual environment..."
    cd ..
    python3 -m venv venv
    cd langchain-rag-tutorial
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "📚 Installing dependencies..."
source ../venv/bin/activate

# Install all requirements
pip install --upgrade pip
pip install -r requirements.txt

echo "🔍 Verifying installations..."

# Check critical packages
python -c "import langchain; print('✅ LangChain installed')" || echo "❌ LangChain not installed"
python -c "import openai; print('✅ OpenAI installed')" || echo "❌ OpenAI not installed"
python -c "import telegram; print('✅ Telegram bot installed')" || echo "❌ Telegram bot not installed"
python -c "import discord; print('✅ Discord bot installed')" || echo "❌ Discord bot not installed"
python -c "import chromadb; print('✅ ChromaDB installed')" || echo "❌ ChromaDB not installed"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Telegram Bot Configuration  
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
EOF
    echo "📝 Please edit .env file with your actual API keys"
else
    echo "✅ .env file exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys (if not done already)"
echo "2. Run: python create_docs_database.py (to create vector database)"
echo "3. Run: python telegram_bot_rag.py (to start Telegram bot)"
echo "   or: python discord_bot_rag.py (to start Discord bot)"
