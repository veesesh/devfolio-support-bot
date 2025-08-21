#!/usr/bin/env python3
"""
Telegram Bot with RAG Integration - Step 3
This version integrates with your RAG system and only responds when mentioned in groups.
"""

import logging
import argparse
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# RAG Configuration
CHROMA_PATH_DOCS = "chroma_docs"  # Documentation database
ORGANIZER_USERNAME = "@vee19tel"  # Organizer to tag when uncertain

# Confidence threshold - lower means more strict
CONFIDENCE_THRESHOLD = 0.65
MIN_CONTEXT_LENGTH = 200  # Minimum context length for confident answers

# Prompt for generating multiple queries
QUERY_GENERATION_TEMPLATE = """
You are an expert at generating search queries for a Devfolio hackathon documentation knowledge base.

Given the user's original question, generate up to 3 diverse but related search queries that would help retrieve comprehensive information to answer the question.

Make the queries:
1. More specific and focused on different aspects
2. Use different keywords and phrasings
3. Be concise but descriptive

Original Question: {original_query}

Generate queries in this format:
1. [query 1]
2. [query 2]
3. [query 3]

Only generate the numbered list, no other text.
"""

PROMPT_TEMPLATE = """
Answer the question based only on the following context about hackathons and Devfolio platform:

{context}

---

Answer the question based on the above context: {question}

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS:
1. Start with a friendly greeting (Hi Builder! 👋)
2. Provide a short paraphrased answer (1-2 sentences)
3. Break down the solution into clear steps using "**Steps:**" heading
4. Use numbered steps (1., 2., 3., etc.)
5. Do not put title like-> a short answer: and give solution. 
6. Understand the users POV ( how a human would like to read through the help message)

EXAMPLE FORMAT:
Hi builder! 👋 

[Short answer in 1-2 sentences]

**Steps:**
1. [First step]
2. [Second step] 
3. [Third step]

IMPORTANT RULES:
- If the context doesn't contain enough specific information, respond with "UNCERTAIN"
- If you can answer but are not completely confident, start with "PARTIAL:"
- Only give confident answers when context clearly addresses the question
- Keep steps concise and actionable
- Use simple, clear language
"""

CONFIDENCE_EVALUATION_PROMPT = """
Based on the following context and question, evaluate how confident you can be in providing an accurate answer.

Context: {context}
Question: {question}

Rate your confidence level:
- HIGH: Context directly and comprehensively answers the question
- MEDIUM: Context partially answers the question but some details may be missing
- LOW: Context contains little relevant information or is too general

Respond with only: HIGH, MEDIUM, or LOW
"""

def evaluate_confidence(query_text: str, context_text: str) -> str:
    """Evaluate confidence level for the given context and question."""
    try:
        prompt_template = ChatPromptTemplate.from_template(CONFIDENCE_EVALUATION_PROMPT)
        prompt = prompt_template.format(context=context_text, question=query_text)
        
        model = ChatOpenAI(temperature=0)  # Lower temperature for more consistent evaluation
        confidence_level = model.invoke(prompt).content.strip().upper()
        
        return confidence_level if confidence_level in ['HIGH', 'MEDIUM', 'LOW'] else 'LOW'
    except Exception as e:
        logger.error(f"Confidence evaluation error: {e}")
        return 'LOW'

def query_rag_system(query_text: str, use_docs: bool = True) -> str:
    """Query the RAG system and return formatted response with sources."""
    try:
        # Use documentation database
        chroma_path = CHROMA_PATH_DOCS
        
        # Prepare the DB
        embedding_function = OpenAIEmbeddings()
        db = Chroma(persist_directory=chroma_path, embedding_function=embedding_function)

        # First try with original query to check confidence
        print("Testing initial query confidence...")
        initial_results = db.similarity_search_with_relevance_scores(query_text, k=4)
        
        # Check if we got high confidence results from initial query
        high_confidence_threshold = 0.65  # Threshold for considering a result high confidence
        has_high_confidence = any(score > high_confidence_threshold for _, score in initial_results)
        
        if not has_high_confidence:
            print("No high-confidence matches found for the initial query.")
            # For low confidence, directly return without generating multiple queries
            return f"🤔 I couldn't find relevant information for your question in the documentation.\n\n{ORGANIZER_USERNAME} Could you help with this question?"
            
        # Since we have high confidence matches, generate up to 3 related queries
        prompt_template = ChatPromptTemplate.from_template(QUERY_GENERATION_TEMPLATE)
        prompt = prompt_template.format(original_query=query_text)
        
        model = ChatOpenAI(temperature=0.3)
        response = model.invoke(prompt).content
        
        # Parse the queries (up to 3)
        queries = []
        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                query = line.split('.', 1)[-1].strip().lstrip('•-').strip()
                if query and len(query) > 3:
                    queries.append(query)
                if len(queries) >= 3:  # Limit to 3 queries
                    break
        
        # Always include original query
        if query_text not in queries:
            queries.insert(0, query_text)
        
        # Search with all queries
        all_results = []
        seen_content = set()
        
        for query in queries:
            results = db.similarity_search_with_relevance_scores(query, k=3)  # Reduced from 4 to 3 per query
            for doc, score in results:
                content_hash = hash(doc.page_content[:100])
                if content_hash not in seen_content and score > 0.4:
                    seen_content.add(content_hash)
                    all_results.append((doc, score))
        
        # Sort by relevance score and get only good results
        all_results.sort(key=lambda x: x[1], reverse=True)
        good_results = [(doc, score) for doc, score in all_results if score > 0.5]
        
        if not good_results:
            return f"🤔 I couldn't find good matches for your question in the documentation.\n\n{ORGANIZER_USERNAME} Could you help with this question?"
            
        # Use only top 4 results for context
        results = good_results[:4]

        # Prepare context
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        
        # Check context length
        if len(context_text) < MIN_CONTEXT_LENGTH:
            return f"🤔 I found limited information for your question.\n\n{ORGANIZER_USERNAME} This might need human expertise!"
        
        # Evaluate confidence
        confidence_level = evaluate_confidence(query_text, context_text)
        logger.info(f"Confidence level: {confidence_level}")
        
        # If confidence is low, tag organizer
        if confidence_level == 'LOW':
            return f"🤔 I found some information but I'm not confident about the answer to avoid giving incorrect details.\n\n{ORGANIZER_USERNAME} Could you help with this question: '{query_text}'?"

        # Prepare context and query
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)

        # Get AI response
        model = ChatOpenAI()
        response_text = model.invoke(prompt).content
        
        # Check if AI is uncertain
        if "UNCERTAIN" in response_text:
            return f"🤔 I don't have enough specific information to answer your question confidently.\n\n{ORGANIZER_USERNAME} Could you help with: '{query_text}'?"
        
        # Handle partial confidence
        confidence_prefix = ""
        if response_text.startswith("PARTIAL:"):
            response_text = response_text.replace("PARTIAL:", "").strip()
            if confidence_level == 'MEDIUM':
                confidence_prefix = "⚠️ *Partial answer* (some details might be missing):\n\n"

        # Format sources for Telegram
        if use_docs:
            base_url = "https://guide.devfolio.co/"
            sources = []
            for doc, _score in results:
                source_path = doc.metadata.get("source", "")
                if source_path:
                    url_path = source_path.replace("data/", "").replace(".mdx", "").replace(".md", "")
                    full_url = base_url + url_path
                    file_name = source_path.split("/")[-1].replace(".mdx", "").replace(".md", "")
                    readable_title = file_name.replace("-", " ").title()
                    sources.append(f"• [{readable_title}]({full_url})")
            
            # Remove duplicates
            unique_sources = list(dict.fromkeys(sources))
            sources_text = "\n".join(unique_sources[:3])  # Limit to 3 sources for Telegram
            
            # Add confidence indicator
            confidence_indicator = ""
            if confidence_level == 'MEDIUM':
                confidence_indicator = "\n\n💡 *If you need more specific details, feel free to ask* " + ORGANIZER_USERNAME
            
            return f"{confidence_prefix}{response_text}\n\n**Refer:** docs for more details\n{sources_text}{confidence_indicator}"
        else:
            return f"{confidence_prefix}{response_text}"

    except Exception as e:
        logger.error(f"RAG query error: {e}")
        return f"❌ Sorry, I encountered an error while processing your question.\n\n{ORGANIZER_USERNAME} Could you help with this technical issue?"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    user = update.effective_user
    message_text = update.message.text
    chat_type = update.effective_chat.type
    
    # Get bot info
    bot_username = context.bot.username
    
    # Log the message
    logger.info(f"Message from {user.first_name} in {chat_type}: {message_text}")
    
    # Only respond in groups - ignore private messages
    if chat_type == 'private':
        logger.info(f"Ignoring private message from {user.first_name}")
        await update.message.reply_text(
            "👋 Hi! I only work in groups to help with hackathon questions.\n\n"
            
            "💡 It’s always recommended to ask questions in public — it helps others who might have the same question and keeps the conversation more engaging.  \n\n"
            "🙌 And if you ever get stuck, someone from our team will be happy to jump in and help with the context."
            f"Example: @{bot_username} How do I organize a hackathon?"
        )
        return
    
    # In groups, only respond if bot is mentioned
    if chat_type in ['group', 'supergroup']:
        bot_mentioned = False
        
        # Check for @botusername mention
        if f"@{bot_username}" in message_text:
            bot_mentioned = True
            # Remove the mention from the message
            message_text = message_text.replace(f"@{bot_username}", "").strip()
        
        # Check if message is a reply to bot's message
        if update.message.reply_to_message and update.message.reply_to_message.from_user.is_bot:
            bot_mentioned = True
        
        # If bot is not mentioned in group, ignore the message
        if not bot_mentioned:
            logger.info(f"Bot not mentioned in group message, ignoring...")
            return
    
    # If no question provided
    if not message_text.strip():
        response = f"Hello {user.first_name}! Ask me anything about hackathons, Devfolio, or project development!"
        await update.message.reply_text(response)
        return
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Query RAG system
    logger.info(f"Querying RAG system with: {message_text}")
    response = query_rag_system(message_text, use_docs=True)
    
    # Send response
    await update.message.reply_text(response, parse_mode='Markdown', disable_web_page_preview=True)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')

def main() -> None:
    """Start the bot."""
    # Get bot token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        print("\n🚨 ERROR: Please add TELEGRAM_BOT_TOKEN to your .env file")
        return

    # Check if RAG databases exist
    if not os.path.exists(CHROMA_PATH_DOCS):
        print(f"\n⚠️  WARNING: {CHROMA_PATH_DOCS} not found!")
        print("Run 'python create_docs_database.py' first to create the documentation database.")
        return

    # Create the Application
    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Starting RAG-integrated bot...")
    print("🤖 RAG-integrated Telegram bot is starting...")
    print("📋 Bot behavior:")
    print("   • Groups ONLY: Responds when mentioned (@botname) in public/private groups")
    print("   • Private DMs: Politely redirects users to use bot in groups")
    print("   • Searches Devfolio documentation for answers")
    print("   • Provides clickable source links")
    print("   • Tags organizer (@vee19tel) when uncertain")
    print("   • Uses confidence evaluation to avoid wrong answers")
    print("\n🔗 Add the bot to a group and mention it to test!")
    print("   Example: '@yourbotname How do I organize a hackathon?'")
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
