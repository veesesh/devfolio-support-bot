# Devfolio Support Bot

A support bot integrated with RAG system using LangChain, OpenAI, and ChromaDB designed for Devfolio, aimed at handling queries and assisting users with common support-related issues.

Includes command-line interface and Telegram & Discord bots for interactive Q&A about hackathons and Devfolio platform.

## 🎯 What This Does

- Loads documentation files (.md, .mdx) and creates searchable vector database
- Provides intelligent Q&A with source links to live documentation
- Includes Telegram & Discord bots with confidence evaluation and organizer tagging

## 🚀 Quick Setup

### **1. Prerequisites**

- Python 3.8+
- Git
- OpenAI API account
- Telegram account (for bot)

### **2. Clone & Setup**

```bash
git clone https://github.com/veesesh/langchain-rag-tutorial.git

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
pip install "unstructured[md]"
python -c "import nltk; nltk.download('punkt_tab'); nltk.download('averaged_perceptron_tagger_eng')"
```

### **4. Environment Configuration**

Create `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
DISCORD_BOT_TOKEN=your_discord_bot_token_here
```

### **5. Create Database**

```bash
python create_docs_database.py
```

### **6. Test the System**

**Command line:**

```bash
python query_docs.py "how to organize hackathon"
```

**Telegram bot:**

```bash
python telegram_bot_rag.py
```

**Discord bot:**

```bash
python discord_bot_rag.py
```

### **7. Common Issues**

- **NLTK errors**: Run the nltk download command
- **API errors**: Check your .env file
- **Import errors**: Ensure virtual environment is activated
- **No results**: Make sure database is created first

## 🤖 Getting API Keys

### OpenAI API Key (Required)

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create account → API Keys → Create new secret key
3. Copy the key (starts with `sk-`)

### Telegram Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy the token

### Discord Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create New Application → Bot → Add Bot
3. Copy the token
4. **Enable "Message Content Intent"** in Bot settings

### Documentation Collection (`data/docs/`)

- Contains hackathon and Devfolio platform documentation
- Use `create_docs_database.py` and `query_docs.py` for this collection

## 📋 Prerequisites

- Python 3.8+
- OpenAI API account and API key
- Virtual environment (recommended)
- **System dependencies for ChromaDB:**
  - Ubuntu/Debian: `sudo apt install python3-dev python3.12-dev build-essential`
  - CentOS/RHEL: `sudo yum install python3-devel gcc gcc-c++`
  - macOS: `xcode-select --install`
  - Windows: Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

### � Troubleshooting

### Module Import Errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### ChromaDB Compilation Errors

```bash
# Install system dependencies first
# Ubuntu/Debian:
sudo apt install python3-dev python3.12-dev build-essential

# macOS:
xcode-select --install

# Then reinstall
pip install -r requirements.txt
```

### API Key Issues

- Check `.env` file exists with correct keys
- Verify OpenAI API key starts with `sk-`
- Ensure no extra spaces in `.env` file

### No Search Results

- Make sure database is created: `python create_docs_database.py`
- Try broader search terms
- Check `data/docs/` contains documentation files

### Bot Not Responding

- Bot must be mentioned: `@botname question`
- Discord: Enable "Message Content Intent" in bot settings
- Check API tokens in `.env` file

## 📚 More Resources

- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Telegram Bot Tutorial](https://core.telegram.org/bots/tutorial)
- [Discord Bot Guide](https://discordpy.readthedocs.io/)
