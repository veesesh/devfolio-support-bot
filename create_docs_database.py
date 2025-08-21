# from langchain.document_loaders import DirectoryLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
# from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import openai 
from dotenv import load_dotenv
import os
import shutil

# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
#---- Set OpenAI API key 
# Change environment variable name from "OPENAI_API_KEY" to the name given in 
# your .env file.
openai.api_key = os.environ['OPENAI_API_KEY']
# openai.api_key = os.getenv("OPENAI_API_KEY")


CHROMA_PATH = "chroma_docs"  # Separate database for docs
DATA_PATH = "data/docs"


def main():
    generate_data_store()


def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)


def load_documents():
    documents = []
    
    # Load .md files
    md_loader = DirectoryLoader(DATA_PATH, glob="**/*.md", recursive=True)
    md_docs = md_loader.load()
    documents.extend(md_docs)
    
    # Load .mdx files  
    mdx_loader = DirectoryLoader(DATA_PATH, glob="**/*.mdx", recursive=True)
    mdx_docs = mdx_loader.load()
    documents.extend(mdx_docs)
    
    print(f"Loaded {len(documents)} documentation files from {DATA_PATH}")
    return documents


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1600,     # Increased for better context preservation
        chunk_overlap=500,   # Larger overlap to maintain continuity
        length_function=len,
        add_start_index=True,
        # Add separators optimized for markdown/mdx
        separators=[
            "\n## ",      # Markdown headers
            "\n### ",     # Sub-headers
            "\n#### ",    # Sub-sub-headers
            "\n\n",       # Paragraph breaks
            "\n",         # Line breaks
            " ",          # Spaces
            ""            # Characters
        ]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    if len(chunks) > 0:
        document = chunks[0] if len(chunks) > 0 else None
        if document:
            print("Sample chunk:")
            print(document.page_content[:300] + "...")
            print(f"Chunk length: {len(document.page_content)} characters")
            print(f"Metadata: {document.metadata}")

    return chunks


def save_to_chroma(chunks: list[Document]):
    # Clear out the database first with better error handling
    if os.path.exists(CHROMA_PATH):
        try:
            print(f"Removing existing database at {CHROMA_PATH}...")
            shutil.rmtree(CHROMA_PATH)
            print("✅ Successfully removed old database")
        except PermissionError as e:
            print(f"⚠️  Permission error removing {CHROMA_PATH}: {e}")
            print("💡 Try stopping any running bots or processes using the database")
            print("💡 Or run: sudo rm -rf chroma_docs")
            return
        except OSError as e:
            print(f"⚠️  OS error removing {CHROMA_PATH}: {e}")
            print("💡 The directory might be in use. Stop the bot and try again.")
            return
        except Exception as e:
            print(f"❌ Unexpected error removing {CHROMA_PATH}: {e}")
            return

    # Create a new DB from the documents.
    try:
        print("Creating new ChromaDB database...")
        db = Chroma.from_documents(
            chunks, OpenAIEmbeddings(), persist_directory=CHROMA_PATH
        )
        db.persist()
        print(f"✅ Saved {len(chunks)} chunks to {CHROMA_PATH}.")
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        print("💡 Make sure your OpenAI API key is set correctly in .env file")


if __name__ == "__main__":
    main()
