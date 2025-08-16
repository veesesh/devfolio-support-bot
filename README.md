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

⚠️ **Important**: Never commit your `.env` file to version control!

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

### Bot Features

#### 🧠 **Smart Confidence System**

The bot uses intelligent confidence evaluation to provide accurate responses:

- **✅ High Confidence**: Provides complete answers with source links
- **⚠️ Medium Confidence**: Gives partial answers with warnings and suggests contacting organizer
- **🤔 Low/No Confidence**: Tags the organizer (@vee19tel) for human assistance

#### 🎯 **Group-Friendly Behavior**

- **Private Chats**: Responds to all messages
- **Groups**: Only responds when mentioned (`@botname question`)
- **Mention Detection**: Recognizes both direct mentions and replies to bot messages

#### 📚 **Intelligent Document Search**

- Searches through 78+ hackathon documentation files
- Provides clickable links to live documentation
- Shows relevance scores for debugging
- Uses optimized chunking for better context

### Sample Telegram Bot Interactions

#### High Confidence Response:
```
User: @hackathonbot How do I submit a project to a hackathon?

Bot: To submit a project to a hackathon on Devfolio, follow these steps:

1. Head to your Hackathon Dashboard and click "Add Project"
2. Fill in all required details including project name, tagline, technologies used
3. Add your GitHub repository, demo video, and screenshots
4. Click "Publish Project" to finalize your submission

📚 Sources:
• [Project Submission](https://guide.devfolio.co/docs/guide/participating-in-hackathons/project-submission)
• [Judging](https://guide.devfolio.co/docs/guide/participating-in-hackathons/judging-1)
```

#### Medium Confidence Response:
```
User: @hackathonbot What are the best practices for winning hackathons?

Bot: ⚠️ Partial answer (some details might be missing):

Based on the documentation, here are some key practices:
- Engage with the community early
- Ask questions during the event
- Maintain good documentation
- Focus on solving real problems
- Present your solution clearly

📚 Sources:
• [Participating In Hackathons](https://guide.devfolio.co/docs/guide/participating-in-hackathons)

💡 If you need more specific details, feel free to ask @vee19tel
```

#### Low Confidence Response:
```
User: @hackathonbot How much should I budget for organizing a 500-person hackathon?

Bot: 🤔 I found some information but I'm not confident about the answer to avoid giving incorrect details.

@vee19tel Could you help with this question: 'How much should I budget for organizing a 500-person hackathon?'
```

### Testing the Bot

#### **High Confidence Questions** (should answer confidently):
- "How do I apply to an offline hackathon?"
- "What are the different hackathon modes?"
- "How do I claim my hackathon schwag?"

#### **Medium Confidence Questions** (partial answers):
- "What should I include in my demo video?"
- "How do I make my Devfolio profile stand out?"

#### **Low Confidence Questions** (should tag organizer):
- "What are the legal requirements for organizing hackathons?"
- "How much does it cost to host on Devfolio?"

## 🗃️ Working with Document Collections

### Option 1: Books Collection (Literary Texts)

```bash
python create_database.py
```

Expected output:

```
Split 1 documents into 801 chunks.
[Sample chunk content...]
Saved 801 chunks to chroma.
```

#### Query the Database

```bash
python query_data.py "How does Alice meet the Mad Hatter?"
```

Expected output:

```
Answer the question based only on the following context:
[Retrieved context...]
Response: [AI-generated answer based on context]
Sources: ['data/books/alice_in_wonderland.md', ...]
```

### Option 2: Documentation Collection (Technical Docs)

#### Create the Documentation Database

```bash
python create_docs_database.py
```

Expected output:

```
Loaded 78 documentation files from data/docs
Split 78 documents into 257 chunks.
[Sample chunk content...]
Saved 257 chunks to chroma_docs.
```

#### Query the Documentation

```bash
python query_docs.py "how to organize university hackathon"
```

Expected output:

```
RELEVANCE SCORES:
1. setting-up-a-hackathon-for-universities.mdx: 0.768
[More scores...]

Response: [AI-generated answer with step-by-step guidance]

Sources:
- [Setting Up A Hackathon For Universities](https://guide.devfolio.co/docs/guide/setting-up-a-hackathon-for-universities)
- [Modes](https://guide.devfolio.co/docs/guide/modes)
[More clickable links...]
```

[Retrieved context...]
Response: [AI-generated answer based on context]
Sources: ['data/books/alice_in_wonderland.md', ...]

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

## 📁 Project Structure

```
langchain-rag-tutorial/
├── data/
│   ├── books/
│   │   └── alice_in_wonderland.md           # Literary source document
│   └── docs/
│       └── guide/                           # Hackathon documentation (.mdx files)
│           ├── setting-up-a-hackathon-for-universities.mdx
│           ├── modes.mdx
│           ├── apply-with-devfolio-integration.mdx
│           └── [78+ other documentation files]
├── chroma/                                  # Books vector database
├── chroma_docs/                             # Documentation vector database
├── .env                                     # OpenAI API key (create this)
├── .gitignore                               # Git ignore file
├── telegram_bot_basic.py                   # Basic Telegram bot (echo responses)
├── telegram_bot_group_friendly.py          # Group-friendly bot (mention detection)
├── telegram_bot_rag.py                     # Full RAG-integrated bot with confidence evaluation
├── create_database.py                       # Script to create books database
├── query_data.py                            # Script to query books database
├── query_docs.py                            # Script to query documentation database
├── compare_embeddings.py                    # Utility to compare embeddings
├── analyze_chunks.py                        # Utility to analyze chunking strategies
├── requirements.txt                         # Python dependencies
└── README.md                                # This file
```

├── create_database.py # Script to create vector database
├── query_data.py # Script to query the database
├── compare_embeddings.py # Utility to compare embeddings
├── requirements.txt # Python dependencies
└── README.md # This file

````

## 🛠️ Customization

### Adding Your Own Documents

**For Books/Literary Texts:**
1. Place markdown files in `data/books/`
2. Run `python create_database.py` to recreate the database
3. Query using `python query_data.py "your question"`

**For Documentation:**
1. Place .md or .mdx files in `data/docs/`
2. Run `python create_docs_database.py` to recreate the database
3. Query using `python query_docs.py "your question"`

### Optimized Chunking Strategy

The documentation database uses improved chunking optimized for technical content:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,     # Larger chunks for better context
    chunk_overlap=150,   # More overlap for continuity
    separators=[
        "\n## ",         # Markdown headers
        "\n### ",        # Sub-headers
        "\n#### ",       # Sub-sub-headers
        "\n\n",          # Paragraph breaks
        "\n",            # Line breaks
        " ",             # Spaces
        ""               # Characters
    ]
)
````

### Telegram Bot Configuration

#### Setting the Organizer Username

To change the organizer who gets tagged when the bot is uncertain, modify `telegram_bot_rag.py`:

```python
ORGANIZER_USERNAME = "@your_username"  # Change this to your Telegram username
```

#### Adjusting Confidence Thresholds

Fine-tune the bot's confidence evaluation:

```python
CONFIDENCE_THRESHOLD = 0.65    # Lower = more strict, higher = more permissive
MIN_CONTEXT_LENGTH = 200       # Minimum context length for confident answers
```

#### Customizing Bot Responses

Modify response templates in `telegram_bot_rag.py`:

```python
# For uncertain responses
return f"🤔 I found some information but I'm not confident about the answer to avoid giving incorrect details.\n\n{ORGANIZER_USERNAME} Could you help with this question: '{query_text}'?"

# For partial responses  
confidence_prefix = "⚠️ *Partial answer* (some details might be missing):\n\n"
```

### Clickable Documentation Links

- **Base URL**: `https://guide.devfolio.co/`
- **Path Conversion**: `data/docs/guide/modes.mdx` → `https://guide.devfolio.co/docs/guide/modes`
- **Format**: `[Readable Title](URL)` for easy navigation

To customize the base URL, modify the `base_url` variable in `query_docs.py`:

```python
base_url = "https://your-docs-site.com/"
```

### Adjusting Chunk Size

In `create_database.py` (for books), modify:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,      # Increase for larger chunks
    chunk_overlap=100,   # Adjust overlap
    length_function=len,
    add_start_index=True,
)
```

### Changing Relevance Threshold

In `query_data.py`, modify:

```python
if len(results) == 0 or results[0][1] < 0.7:  # Lower for more results
```

### Using Different Models

Replace `ChatOpenAI()` with other models:

```python
model = ChatOpenAI(model="gpt-4")  # Use GPT-4
# or
model = ChatOpenAI(model="gpt-3.5-turbo-16k")  # For longer contexts
```

## � Example Use Cases

### Documentation Queries

Perfect for technical documentation, guides, and how-to content:

```bash
# Hackathon organization
python query_docs.py "how to organize university hackathon"
python query_docs.py "what are the different hackathon modes"
python query_docs.py "how to integrate apply with devfolio button"

# Platform features
python query_docs.py "how does judging work on devfolio"
python query_docs.py "what is quadratic voting"
python query_docs.py "how to set up offline judging"
```

### Literary Queries

Great for educational content, literature analysis, and creative writing:

```bash
# Character analysis
python query_data.py "How does Alice meet the Mad Hatter?"
python query_data.py "What is the Cheshire Cat's role in the story?"

# Plot understanding
python query_data.py "What happens at the tea party?"
python query_data.py "How does Alice fall down the rabbit hole?"
```

## 🚀 Advanced Features

### Relevance Score Debugging

The documentation query system shows relevance scores to help you understand result quality:

```
RELEVANCE SCORES:
1. setting-up-a-hackathon-for-universities.mdx: 0.768
2. modes.mdx: 0.753
3. judging-1.mdx: 0.751
```

### Automatic Link Generation

Sources are automatically converted to clickable documentation links:

```
Sources:
- [Setting Up A Hackathon For Universities](https://guide.devfolio.co/docs/guide/setting-up-a-hackathon-for-universities)
- [Modes](https://guide.devfolio.co/docs/guide/modes)
```

### Smart Chunk Analysis

Use the included analysis tool to optimize chunking for your content:

```bash
python analyze_chunks.py
```

## �🔍 Edge Cases and Limitations

### 1. Large Documents

- **Issue**: Very large documents may exceed token limits
- **Solution**: Adjust chunk_size or use streaming

### 2. Non-English Text

- **Issue**: NLTK tokenizers are English-focused
- **Solution**: Configure language-specific tokenizers

### 3. Special Characters

- **Issue**: Some markdown formatting may cause parsing issues
- **Solution**: Preprocess documents to clean formatting

### 4. API Rate Limits

- **Issue**: OpenAI API has rate limits
- **Solution**: Implement retry logic and respect rate limits

### 5. Memory Usage

- **Issue**: Large vector databases consume significant memory
- **Solution**: Use ChromaDB's persistent storage efficiently

### 6. Network Issues

- **Issue**: API calls may fail due to network problems
- **Solution**: Implement error handling and retries

## 📚 Additional Resources

- [Original Tutorial Video](https://www.youtube.com/watch?v=tcqEUSNCn8I&ab_channel=pixegami)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
