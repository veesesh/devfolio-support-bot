# Setup Guide - Requirements & Dependencies

## 📋 System Requirements

Before installing Python packages, ensure you have the required system dependencies:

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install python3-dev python3.12-dev build-essential
```

### CentOS/RHEL

```bash
sudo yum install python3-devel gcc gcc-c++
```

### macOS

```bash
xcode-select --install
```

### Windows

- Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

## 🐍 Python Environment Setup

1. **Create virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Upgrade pip:**

   ```bash
   pip install --upgrade pip
   ```

3. **Install requirements:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install markdown support:**
   ```bash
   pip install "unstructured[md]"
   ```

## 🔧 Common Issues & Solutions

### Issue: `chroma-hnswlib` compilation fails

**Solution:** Install Python development headers (see system requirements above)

### Issue: `onnxruntime` issues on macOS

**Solution:** Use conda instead:

```bash
conda install onnxruntime -c conda-forge
```

### Issue: Module import errors

**Solution:** Ensure virtual environment is activated and all packages installed

## ✅ Verification

Test your installation:

```bash
python -c "
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from telegram import Update
import discord
print('✓ All modules imported successfully!')
"
```

## 📦 Installed Packages

The requirements.txt includes:

- **Core RAG:** langchain, langchain-community, langchain-openai
- **Vector Storage:** chromadb, chroma-hnswlib
- **Document Processing:** unstructured, markdown support
- **AI Integration:** openai, tiktoken
- **Bot Frameworks:** python-telegram-bot, discord.py
- **Utilities:** python-dotenv, and various dependencies

Total packages installed: ~130 (including dependencies)

## 🚀 Next Steps

1. Create `.env` file with your API keys
2. Run `python create_docs_database.py` to create vector database
3. Test with `python query_docs.py "your question"`
4. Optional: Run bots with `python telegram_bot_rag.py` or `python discord_bot_rag.py`
