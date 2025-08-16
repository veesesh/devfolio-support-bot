from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from dotenv import load_dotenv
import os

load_dotenv()

def analyze_chunks():
    # Load a few sample documents
    loader = DirectoryLoader("data/docs", glob="**/*.mdx", recursive=True)
    documents = loader.load()
    
    print(f"Loaded {len(documents)} documents")
    
    # Test different chunk sizes
    chunk_sizes = [300, 500, 800, 1200]
    
    for chunk_size in chunk_sizes:
        print(f"\n{'='*60}")
        print(f"TESTING CHUNK SIZE: {chunk_size}")
        print(f"{'='*60}")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=100,
            length_function=len,
            add_start_index=True,
        )
        
        chunks = text_splitter.split_documents(documents[:3])  # Test with first 3 docs
        
        print(f"Split {len(documents[:3])} documents into {len(chunks)} chunks")
        
        # Show some sample chunks
        for i, chunk in enumerate(chunks[:3]):
            print(f"\n--- Chunk {i+1} (Length: {len(chunk.page_content)}) ---")
            print(f"Source: {chunk.metadata.get('source', 'Unknown')}")
            print(f"Content preview: {chunk.page_content[:200]}...")
            if len(chunk.page_content) > 200:
                print(f"Content end: ...{chunk.page_content[-100:]}")
            print()

if __name__ == "__main__":
    analyze_chunks()
