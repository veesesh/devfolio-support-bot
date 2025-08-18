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

## 🚀 Complete Setup Guide for New Users

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/langchain-rag-tutorial.git
cd langchain-rag-tutorial
```

### Step 2: Check Python Version

Ensure you have Python 3.8 or higher:

```bash
python --version
# Should show Python 3.8+ (e.g., Python 3.10.12)
```

If you don't have Python 3.8+, install it from [python.org](https://python.org).

### Step 3: Create Virtual Environment

**⚠️ IMPORTANT: Always use a virtual environment to avoid dependency conflicts!**

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) at the beginning of your command prompt
```

### Step 4: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install core dependencies
pip install -r requirements.txt

# Install markdown support (required for document processing)
pip install "unstructured[md]"
```

**Platform-Specific Notes:**

- **macOS Users**: If you get `onnxruntime` errors, use conda:

  ```bash
  conda install onnxruntime -c conda-forge
  ```

- **Windows Users**: Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) first if you encounter compilation errors.

### Step 5: Download NLTK Data

```bash
python -c "import nltk; nltk.download('punkt_tab'); nltk.download('averaged_perceptron_tagger_eng')"
```

Expected output:

```
[nltk_data] Downloading package punkt_tab to [path]...
[nltk_data]   Package punkt_tab is already up-to-date!
[nltk_data] Downloading package averaged_perceptron_tagger_eng to [path]...
[nltk_data]   Package averaged_perceptron_tagger_eng is already up-to-date!
```

### Step 6: Configure API Keys

Create a `.env` file in the project root:

```bash
# Create the file
touch .env  # On Windows: type nul > .env
```

Add your API keys to the `.env` file:

```bash
# Required for RAG functionality
OPENAI_API_KEY=your_openai_api_key_here

# Required only if using Telegram bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

**Getting API Keys:**

1. **OpenAI API Key** (Required):

   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Create account → Go to API Keys → Create new secret key
   - Copy the key (starts with `sk-`)

2. **Telegram Bot Token** (Optional, for bot functionality):
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Send `/newbot`
   - Follow instructions to create your bot
   - Copy the token (format: `123456789:ABCdefGHI...`)

### Step 7: Create Vector Databases

**For Documentation (Recommended to start with):**

```bash
python create_docs_database.py
```

Expected output:

```
Loaded 78 documentation files from data/docs
Split 78 documents into 257 chunks.
Saved 257 chunks to chroma_docs.
```

**For Books (Optional):**

```bash
python create_database.py
```

### Step 8: Test the System

**Test Documentation Queries:**

```bash
python query_docs.py "how to organize a hackathon"
```

**Test Books Queries:**

```bash
python query_data.py "How does Alice meet the Mad Hatter?"
```

### Step 9: Run Telegram Bot (Optional)

If you configured the Telegram bot token:

```bash
python telegram_bot_rag.py
```

You should see:

```
🤖 RAG-integrated Telegram bot is starting...
📋 Bot behavior:
   • Groups ONLY: Responds when mentioned (@botname) in public/private groups
   • Private DMs: Politely redirects users to use bot in groups
   ...
```

## 🛠️ Quick Start

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
The bot has sophisticated behavior:
- 📱 **Groups ONLY**: Only works in public/private groups (Telegram or Discord-style)
- 🔍 **Smart Mention Detection**: Responds when mentioned (@botname) in groups
- 🚫 **No Direct Messages**: Politely redirects private DM attempts to group usage
- 🤖 **RAG Integration**: Searches the documentation database for accurate answers
- 🧠 **Confidence Evaluation**: Three-tier system (HIGH/MEDIUM/LOW confidence)
- 🏷️ **Smart Tagging**: Tags organizer @vee19tel when uncertain (LOW confidence)
- 🔗 **Source Links**: Provides clickable links to relevant documentation

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
