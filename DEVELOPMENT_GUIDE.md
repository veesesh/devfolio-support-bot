# Development Best Practices

## 🛡️ Preventing Common Issues

### 1. **Always Use Virtual Environments**

```bash
# Create virtual environment
python -m venv venv

# Activate it EVERY TIME you work on the project
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 2. **Run Dependency Checks First**

Before running any bot or script:

```bash
python check_dependencies.py
```

This will tell you exactly what's missing or misconfigured.

### 3. **Use the Setup Script for New Environments**

```bash
./setup.sh
```

This automates:

- Virtual environment creation
- Package installation
- Dependency verification
- Environment file setup

### 4. **Keep Dependencies Updated**

When you update packages, also update the requirements.txt:

```bash
pip freeze > requirements.txt
```

### 5. **Environment File Management**

Never commit your `.env` file with real API keys. Keep a template:

```bash
# Copy template for new setup
cp .env.template .env
# Then edit with real keys
```

### 6. **Database Management**

Always ensure the vector database exists before running bots:

```bash
python create_docs_database.py
```

## 🔧 Troubleshooting Workflow

1. **Check Python environment**: `python check_dependencies.py`
2. **Verify virtual environment**: `which python` should show venv path
3. **Check package versions**: `pip list | grep langchain`
4. **Test imports manually**: `python -c "import telegram; print('OK')"`
5. **Recreate database if needed**: `python create_docs_database.py`

## 📦 Package Version Management

Current working versions (update this when you update packages):

```
langchain==0.2.2
langchain-community==0.2.3
langchain-openai==0.2.5  # Updated to fix OpenAI compatibility
openai==1.31.1
chromadb==0.5.0
python-telegram-bot==21.5
discord.py==2.3.2
```

## 🚨 Common Error Patterns and Solutions

### "No module named 'telegram'"

**Solution**: `pip install python-telegram-bot`

### "OpenAI API key not found"

**Solution**: Check `.env` file has `OPENAI_API_KEY=sk-...`

### "proxies parameter error"

**Solution**: Update `langchain-openai` to version 0.2.5+

### "Vector database not found"

**Solution**: Run `python create_docs_database.py`

### "Permission denied on ChromaDB"

**Solution**: Stop all running bots, then `rm -rf chroma_docs` and recreate

## 🎯 Daily Workflow

1. Activate virtual environment: `source venv/bin/activate`
2. Check dependencies: `python check_dependencies.py`
3. Update code
4. Test locally before deploying
5. Keep requirements.txt updated
