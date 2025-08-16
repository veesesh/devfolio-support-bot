# LangChain RAG Tutorial with Telegram Bot

A comprehensive Retrieval-Augmented Generation (RAG) system using LangChain, OpenAI, and ChromaDB to query documents intelligently. This project includes both command-line interfaces and a Telegram bot for interactive Q&A about hackathons and Devfolio platform.

## 🎯 What This Project Does

This RAG system:

- Loads markdown (.md) and MDX (.mdx) documents from multiple directories
- Splits them into optimized chunks using LangChain's text splitter with markdown-aware separators
- Creates embeddings using OpenAI's embedding model
- Stores embeddings in ChromaDB vector databases
- Allows natural language queries against the document collections
- Returns relevant context with clickable links to live documentation
- Supports both literary texts (Alice in Wonderland) and technical documentation (Devfolio guides)
- **🤖 Includes a Telegram bot with intelligent confidence evaluation and organizer tagging**

## 📂 Available Document Collections

### 1. Books Collection (`data/books/`)

- Contains literary texts like Alice in Wonderland
- Use `create_database.py` and `query_data.py` for this collection

### 2. Documentation Collection (`data/docs/`)

- Contains hackathon and Devfolio platform documentation
- Use `create_docs_database.py` and `query_docs.py` for this collection
- Sources are automatically converted to clickable links to live documentation

## 📋 Prerequisites

- Python 3.8+
- OpenAI API account and API key
- Virtual environment (recommended)

## 🚀 Quick Start

### 1. Environment Setup

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. OpenAI API Key & Telegram Bot Configuration

Create a `.env` file in the project root and add your API keys:

```bash
OPENAI_API_KEY=your_openai_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

**To get a Telegram Bot Token:**
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Choose a name and username for your bot
4. Copy the token and add it to your `.env` file


### 3. Install Dependencies

**Option A: Quick Installation (Recommended)**

```bash
# Install core dependencies
pip install -r requirements.txt

# Install markdown support
pip install "unstructured[md]"

# Download required NLTK data
python -c "import nltk; nltk.download('punkt_tab'); nltk.download('averaged_perceptron_tagger_eng')"
```

**Note**: The requirements.txt now includes `python-telegram-bot` for the Telegram bot functionality.

**Option B: Manual Installation with Compatibility Fixes**

If you encounter dependency conflicts, upgrade to the latest compatible versions:

```bash
# Upgrade core packages to resolve compatibility issues
pip install --upgrade openai langchain langchain-openai langchain-community langchain-text-splitters

# Install remaining dependencies
pip install chromadb python-dotenv unstructured tiktoken

# Install markdown support
pip install "unstructured[md]"

# Download NLTK data
python -c "import nltk; nltk.download('punkt_tab'); nltk.download('averaged_perceptron_tagger_eng')"
```

### 4. Platform-Specific Installation Notes

**macOS Users:**
If you encounter `onnxruntime` installation issues:

```bash
conda install onnxruntime -c conda-forge
```

See [this thread](https://github.com/microsoft/onnxruntime/issues/11037) for additional help.

**Windows Users:**
Install Microsoft C++ Build Tools by following [this guide](https://github.com/bycloudai/InstallVSBuildToolsWindows) before installing dependencies.

## � Telegram Bot Integration

### Running the Telegram Bot

After setting up your databases and configuring the bot token:

```bash
python telegram_bot_rag.py
```

Expected output:
```
🤖 RAG-integrated Telegram bot is starting...
📋 Bot behavior:
   • In private chats: Responds to all messages with RAG
   • In groups: Only responds when mentioned (@botname)
   • Searches Devfolio documentation for answers
   • Provides clickable source links
   • Tags organizer (@vee19tel) when uncertain
   • Uses confidence evaluation to avoid wrong answers

🔗 Add the bot to a private group and mention it to test!
   Example: '@yourbotname How do I organize a hackathon?'
```

````

## 🔧 Common Issues and Troubleshooting

### Environment Variable Issues

**Error**: `Did not find openai_api_key, please add an environment variable OPENAI_API_KEY`

**Solutions**:

1. Ensure your `.env` file exists and contains `OPENAI_API_KEY=your_key`
2. Check that `python-dotenv` is installed
3. Verify the `load_dotenv()` call is present in your Python files

### NLTK Data Missing

**Error**: `Resource punkt_tab not found` or `Resource averaged_perceptron_tagger_eng not found`

**Solution**:

```bash
python -c "import nltk; nltk.download('punkt_tab'); nltk.download('averaged_perceptron_tagger_eng')"
````

### Version Compatibility Issues

**Error**: `Client.__init__() got an unexpected keyword argument 'proxies'`

**Solution**: Upgrade packages to compatible versions:

```bash
pip install --upgrade openai langchain langchain-openai langchain-community
```

### No Results Found

**Error**: `Unable to find matching results.`

**Possible Causes**:

1. Vector database not created - run the appropriate create script first
2. Query too specific - try broader queries
3. Relevance threshold too high - documents must be highly relevant
4. Wrong database - make sure you're using the right query script for your data

### ChromaDB Warnings

**Warning**: Deprecation warnings about `Chroma` class

**Note**: These are warnings about future versions. The code works but consider migrating to `langchain-chroma` package for future compatibility:

```bash
pip install langchain-chroma
```

### Telegram Bot Configuration

#### Setting the Organizer Username

To change the organizer who gets tagged when the bot is uncertain, modify `telegram_bot_rag.py`:

```python
ORGANIZER_USERNAME = "@your_username"  # Change this to your Telegram username
```



