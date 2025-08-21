# Devfolio Support Bot

A support bot integrated with RAG system using LangChain, OpenAI, and ChromaDB designed for Devfolio, aimed at handling queries and assisting users with common support-related issues.

Includes command-line interface and Telegram/Discord bots for interactive Q&A about hackathons and Devfolio platform.

## 🎯 What This Does

- Loads documentation files (.md, .mdx) and creates searchable vector database
- Provides intelligent Q&A with source links to live documentation
- Includes Telegram & Discord bots with confidence evaluation and organizer tagging

## 🚀 Quick Setup

### **1. Prerequisites**

- Python 3.8+
- Git
- OpenAI API account

### **2. Clone & Setup**

```bash
git clone https://github.com/veesesh/devfolio-support-bot
cd devfolio-support-bot
```

### **3. Install UV Package Manager**

install uv package manager according to your os

### **4. Environment Configuration**

Create `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
DISCORD_BOT_TOKEN=your_discord_bot_token_here
```

### **5. Create Database**

```bash
uv run create_docs_database.py
```

### **6. Test the System**

**Command line:**

```bash
uv run query_docs.py "how to organize hackathon"
```

**Telegram bot:**

```bash
uv run telegram_bot_rag.py
```

**Discord bot:**

```bash
uv run discord_bot_rag.py
```

### **7. Common Issues**

- **API errors**: Check your .env file
- **Import errors**: Ensure virtual environment is activated
- **No results**: Make sure database is created first
