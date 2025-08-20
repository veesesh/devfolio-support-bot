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

### **2. Clone & Setup**

```bash
git clone https://github.com/veesesh/devfolio-support-bot
cd devfolio-support-bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
pip install "unstructured[md]"
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

- **API errors**: Check your .env file
- **Import errors**: Ensure virtual environment is activated
- **No results**: Make sure database is created first

## 📚 Documentation Collection

The `data/docs/` directory:

- Contains hackathon and Devfolio platform documentation
- Use `create_docs_database.py` and `query_docs.py` for this collection

## 🔧 Troubleshooting

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

### ChromaDB/ONNX Runtime Issues

If you encounter issues with ONNX Runtime (particularly on macOS):

```bash
# Try this first:
pip install onnxruntime

# If still having issues on macOS, use conda:
conda install onnxruntime -c conda-forge
```
