# LangChain RAG Tutorial

A Retrieval-Augmented Generation (RAG) system using LangChain, OpenAI, and ChromaDB to query documents intelligently. This tutorial demonstrates how to create a vector database from markdown documents and query it using natural language.

## 🎯 What This Project Does

This RAG system:

- Loads markdown documents from the `data/books/` directory
- Splits them into chunks using LangChain's text splitter
- Creates embeddings using OpenAI's embedding model
- Stores embeddings in a ChromaDB vector database
- Allows natural language queries against the document collection
- Returns relevant context and sources for each query

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

### 2. OpenAI API Key Configuration

Create a `.env` file in the project root and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

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

### 5. Create the Vector Database

```bash
python create_database.py
```

Expected output:

```
Split 1 documents into 801 chunks.
[Sample chunk content...]
Saved 801 chunks to chroma.
```

### 6. Query the Database

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
```

### Version Compatibility Issues

**Error**: `Client.__init__() got an unexpected keyword argument 'proxies'`

**Solution**: Upgrade packages to compatible versions:

```bash
pip install --upgrade openai langchain langchain-openai langchain-community
```

### No Results Found

**Error**: `Unable to find matching results.`

**Possible Causes**:

1. Vector database not created - run `python create_database.py` first
2. Query too specific - try broader queries
3. Relevance threshold too high (0.7) - documents must be highly relevant

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
│   └── books/
│       └── alice_in_wonderland.md    # Source document
├── chroma/                           # Vector database (created after running create_database.py)
├── .env                             # OpenAI API key (create this)
├── .gitignore                       # Git ignore file
├── create_database.py               # Script to create vector database
├── query_data.py                    # Script to query the database
├── compare_embeddings.py            # Utility to compare embeddings
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 🛠️ Customization

### Adding Your Own Documents

1. Place markdown files in `data/books/`
2. Run `python create_database.py` to recreate the database
3. Query using `python query_data.py "your question"`

### Adjusting Chunk Size

In `create_database.py`, modify:

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

## 🔍 Edge Cases and Limitations

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
