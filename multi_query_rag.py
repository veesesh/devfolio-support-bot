#!/usr/bin/env python3
"""
Multi-Query RAG System
This implementation uses an LLM to generate multiple related queries before retrieval,
improving the comprehensiveness of retrieved context.

Flow: User Query -> LLM (Generate Multiple Queries) -> Retrieve for Each Query -> Combine Context -> Final Response
"""

import argparse
import os
from dotenv import load_dotenv
from typing import List, Set
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables from .env file
load_dotenv()

CHROMA_PATH = "chroma_docs"  # Documentation database

# Prompt for generating multiple queries
QUERY_GENERATION_TEMPLATE = """
You are an expert at generating search queries for a Devfolio hackathon documentation knowledge base.

Given the user's original question, generate 3-5 diverse but related search queries that would help retrieve comprehensive information to answer the question.

Make the queries:
1. More specific and focused on different aspects
2. Use different keywords and phrasings
3. Cover edge cases or related concepts
4. Be concise but descriptive

Original Question: {original_query}

Generate queries in this format:
1. [query 1]
2. [query 2]
3. [query 3]
4. [query 4]
5. [query 5]

Only generate the numbered list, no other text.
"""

# Main RAG response prompt
RESPONSE_TEMPLATE = """
Answer the question based only on the following context about hackathons and Devfolio platform:

{context}

---

Answer the question based on the above context: {question}

Format your response as follows:

**TL;DR:** [Provide a 2-3 sentence summary of the key points that directly answers the question]

**Step-by-Step Guide:**
1. [First step with brief explanation]
2. [Second step with brief explanation]
3. [Continue with additional steps as needed]
[Only include steps if the question asks for a process or how-to]

**Additional Details:**
[Any additional context, tips, or important information from the documentation]

If the context doesn't contain enough information to answer the question completely, say "I don't have enough information in the provided documentation to fully answer that question, but here's what I can tell you based on the available information:" and then follow the format above.

Be thorough but concise, and organize your response clearly. If the question doesn't require steps (e.g., it's asking for general information), focus on the TL;DR and Additional Details sections.
"""

def generate_multiple_queries(original_query: str) -> List[str]:
    """Generate multiple related queries using LLM."""
    try:
        prompt_template = ChatPromptTemplate.from_template(QUERY_GENERATION_TEMPLATE)
        prompt = prompt_template.format(original_query=original_query)
        
        model = ChatOpenAI(temperature=0.3)  # Slightly creative but consistent
        response = model.invoke(prompt).content
        
        # Parse the numbered list
        queries = []
        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                # Remove numbering and clean up
                query = line.split('.', 1)[-1].strip()
                query = query.lstrip('•-').strip()
                if query and len(query) > 3:  # Ensure meaningful queries
                    queries.append(query)
        
        # Include original query if not already similar
        if original_query not in queries:
            queries.insert(0, original_query)
        
        print(f"Generated {len(queries)} queries:")
        for i, q in enumerate(queries, 1):
            print(f"  {i}. {q}")
        print()
        
        return queries
    
    except Exception as e:
        print(f"Error generating queries: {e}")
        return [original_query]  # Fallback to original query

def retrieve_for_queries(queries: List[str], db, k_per_query: int = 3) -> List[tuple]:
    """Retrieve documents for each query and combine results."""
    all_results = []
    seen_content = set()  # To avoid duplicate documents
    
    print("Retrieving documents for each query:")
    print("=" * 50)
    
    for i, query in enumerate(queries, 1):
        print(f"Query {i}: {query}")
        
        # Search for this specific query
        results = db.similarity_search_with_relevance_scores(query, k=k_per_query)
        
        query_results = []
        for doc, score in results:
            # Use content hash to avoid duplicates
            content_hash = hash(doc.page_content[:100])  # Use first 100 chars as identifier
            if content_hash not in seen_content and score > 0.4:  # Lower threshold for multi-query
                seen_content.add(content_hash)
                all_results.append((doc, score, query))  # Include which query found this
                query_results.append((doc, score))
        
        print(f"  Found {len(query_results)} relevant documents (scores: {[f'{s:.3f}' for _, s in query_results]})")
    
    print(f"\nTotal unique documents retrieved: {len(all_results)}")
    print("=" * 50)
    
    # Sort by relevance score
    all_results.sort(key=lambda x: x[1], reverse=True)
    
    return all_results

def main():
    # Create CLI
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    parser.add_argument("--max-docs", type=int, default=8, help="Maximum documents to use for context")
    parser.add_argument("--queries-per-search", type=int, default=3, help="Documents to retrieve per generated query")
    args = parser.parse_args()
    
    query_text = args.query_text
    max_docs = args.max_docs
    k_per_query = args.queries_per_search

    print("🔍 MULTI-QUERY RAG SYSTEM")
    print("=" * 50)
    print(f"Original Query: {query_text}")
    print("=" * 50)

    # Prepare the DB
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Step 1: Generate multiple related queries
    print("Step 1: Generating multiple related queries...")
    generated_queries = generate_multiple_queries(query_text)
    
    if len(generated_queries) == 0:
        print("Failed to generate queries. Exiting.")
        return

    # Step 2: Retrieve documents for each query
    print("Step 2: Retrieving documents...")
    all_results = retrieve_for_queries(generated_queries, db, k_per_query)

    if len(all_results) == 0:
        print("Unable to find any matching results across all queries.")
        print("You might want to try:")
        print("- Rephrasing your question")
        print("- Using more specific keywords")
        print("- Asking about hackathon organization, Devfolio features, or application processes")
        return

    # Limit to max_docs for context window management
    limited_results = all_results[:max_docs]
    
    # Step 3: Show what was retrieved
    print("Step 3: Documents selected for context:")
    for i, (doc, score, source_query) in enumerate(limited_results, 1):
        source_file = doc.metadata.get("source", "Unknown").split("/")[-1]
        print(f"  {i}. {source_file} (score: {score:.3f}) [from query: {source_query[:50]}...]")
    print()

    # Step 4: Combine context and generate response
    print("Step 4: Generating comprehensive response...")
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score, _query in limited_results])
    
    prompt_template = ChatPromptTemplate.from_template(RESPONSE_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    
    model = ChatOpenAI()
    response_text = model.invoke(prompt).content

    # Step 5: Format and display results
    print("=" * 50)
    print("FINAL RESPONSE:")
    print("=" * 50)
    print(response_text)
    
    # Show sources
    base_url = "https://guide.devfolio.co/"
    formatted_sources = []
    
    for doc, _score, source_query in limited_results:
        source_path = doc.metadata.get("source", None)
        if source_path:
            # Convert file path to URL
            url_path = source_path.replace("data/", "").replace(".mdx", "").replace(".md", "")
            full_url = base_url + url_path
            
            # Get a readable title from the file name
            file_name = source_path.split("/")[-1].replace(".mdx", "").replace(".md", "")
            readable_title = file_name.replace("-", " ").title()
            
            formatted_sources.append(f"[{readable_title}]({full_url}) (via: {source_query[:50]}...)")
        else:
            formatted_sources.append(f"Unknown source (via: {source_query[:50]}...)")
    
    # Remove duplicates while preserving order
    unique_sources = []
    seen = set()
    for source in formatted_sources:
        source_key = source.split("]")[0] + "]"  # Use title part for deduplication
        if source_key not in seen:
            unique_sources.append(source)
            seen.add(source_key)
    
    print("\n" + "=" * 50)
    print("SOURCES:")
    print("=" * 50)
    for source in unique_sources:
        print(f"- {source}")
    
    # Show query performance summary
    print("\n" + "=" * 50)
    print("QUERY PERFORMANCE SUMMARY:")
    print("=" * 50)
    print(f"Original query: {query_text}")
    print(f"Generated queries: {len(generated_queries)}")
    print(f"Total documents found: {len(all_results)}")
    print(f"Documents used for response: {len(limited_results)}")
    print(f"Unique sources: {len(unique_sources)}")

if __name__ == "__main__":
    main()
