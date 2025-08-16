import argparse
import os
from dotenv import load_dotenv
# from dataclasses import dataclass
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables from .env file
load_dotenv()

CHROMA_PATH = "chroma_docs"  # Documentation database

PROMPT_TEMPLATE = """
Answer the question based only on the following context about hackathons and Devfolio platform:

{context}

---

Answer the question based on the above context: {question}

If the context doesn't contain enough information to answer the question, say "I don't have enough information in the provided documentation to answer that question."
"""


def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text

    # Prepare the DB.
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=6)  # Get more results for better context
    if len(results) == 0 or results[0][1] < 0.5:  # Lower threshold for more inclusive results
        print(f"Unable to find matching results. Tried with relevance threshold of 0.5")
        print("You might want to try:")
        print("- Rephrasing your question")
        print("- Using more specific keywords")
        print("- Asking about hackathon organization, Devfolio features, or application processes")
        return

    # Show relevance scores for debugging
    print("=" * 50)
    print("RELEVANCE SCORES:")
    for i, (doc, score) in enumerate(results):
        source_file = doc.metadata.get("source", "Unknown").split("/")[-1]
        print(f"{i+1}. {source_file}: {score:.3f}")
    print("=" * 50)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print("=" * 50)
    print("QUERY:", query_text)
    print("=" * 50)
    print("CONTEXT USED:")
    print(context_text[:500] + "..." if len(context_text) > 500 else context_text)
    print("=" * 50)

    model = ChatOpenAI()
    response_text = model.invoke(prompt).content  # Updated method

    # Convert file paths to live documentation URLs
    base_url = "https://guide.devfolio.co/"
    formatted_sources = []
    
    for doc, _score in results:
        source_path = doc.metadata.get("source", None)
        if source_path:
            # Convert file path to URL
            # Remove 'data/' prefix and '.mdx' extension
            url_path = source_path.replace("data/", "").replace(".mdx", "").replace(".md", "")
            full_url = base_url + url_path
            
            # Get a readable title from the file name
            file_name = source_path.split("/")[-1].replace(".mdx", "").replace(".md", "")
            readable_title = file_name.replace("-", " ").title()
            
            formatted_sources.append(f"[{readable_title}]({full_url})")
        else:
            formatted_sources.append("Unknown source")
    
    # Remove duplicates while preserving order
    unique_sources = []
    seen = set()
    for source in formatted_sources:
        if source not in seen:
            unique_sources.append(source)
            seen.add(source)
    
    formatted_response = f"**Response:** {response_text}\n\n**Sources:**\n" + "\n".join(f"- {source}" for source in unique_sources)
    print(formatted_response)


if __name__ == "__main__":
    main()
