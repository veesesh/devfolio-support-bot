#!/usr/bin/env python3
"""
Telegram Bot with RAG Integration - Test Version
This version handles both DMs and group messages differently.
"""

import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from webhook_logger import log_interaction

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
MIN_CONTEXT_LENGTH = 100  # Minimum context length for confident answers

# Keep existing prompt templates
QUERY_GENERATION_TEMPLATE = """
Generate up to 3 focused search queries for a Devfolio hackathon docs KB.

Guidelines:
- Each query targets a different angle.
- Use concise, descriptive phrasing.
- Prefer product terms and UI labels where relevant.

Original Question: {original_query}

Output ONLY:
1. <query 1>
2. <query 2>
3. <query 3>
"""


PROMPT_TEMPLATE = """
You are Devfolio’s Support Assistant. Answer ONLY using the material below.

[Material]
{context}

[User question]
{question}

Write a Telegram-ready reply that follows these rules:
- Keep it brief: 3–6 numbered points max.
- Start with a greeting Hi Builder! 👋 
- Use simple Markdown: **bold** for key terms, `inline code` for buttons/labels.
- If the material is incomplete, begin with "PARTIAL:" then provide what's known and what's missing.
- Do not invent details or use outside knowledge.
- Do NOT use words like “context”, “material”, or “based on the above” in the reply.
- Do not use emojis in the main answer, only in the greeting or closing.

Format:
1) Direct answer
2) Key steps or settings
3) Requirements/limits
4) Tips or where to check in the product (if applicable)
"""

CONFIDENCE_EVALUATION_PROMPT = """
Evaluate confidence to answer using ONLY the material.

Material:
{context}

Question:
{question}

Respond with ONE word:
- HIGH  = directly and sufficiently answered
- MEDIUM = partly answered; gaps remain
- LOW    = not answered or too generic
"""


def evaluate_confidence(query_text: str, context_text: str) -> str:
    """Evaluate confidence level for the given context and question."""
    try:
        prompt_template = ChatPromptTemplate.from_template(CONFIDENCE_EVALUATION_PROMPT)
        prompt = prompt_template.format(context=context_text, question=query_text)
        
        model = ChatOpenAI(model="gpt-4.1",temperature=0)  # Lower temperature for more consistent evaluation
        confidence_level = model.invoke(prompt).content.strip().upper()
        
        return confidence_level if confidence_level in ['HIGH', 'MEDIUM', 'LOW'] else 'LOW'
    except Exception as e:
        logger.error(f"Confidence evaluation error: {e}")
        return 'LOW'

def query_rag_system(query_text: str, is_private: bool = False) -> str:
    """Query the RAG system and return formatted response with sources."""
    try:
        # Use documentation database
        chroma_path = CHROMA_PATH_DOCS
        
        # Prepare the DB
        embedding_function = OpenAIEmbeddings()
        db = Chroma(persist_directory=chroma_path, embedding_function=embedding_function)

        # First try with original query to check confidence
        initial_results = db.similarity_search_with_relevance_scores(query_text, k=6)
        
        # Check if we got high confidence results from initial query
        high_confidence_threshold = 0.65  # Threshold for considering a result high confidence
        has_high_confidence = any(score > high_confidence_threshold for _, score in initial_results)
        
        if not has_high_confidence:
            if is_private:
                return ("🤔 I couldn't find relevant information for your question in the documentation.\n\n"
                       "💡 For better support, consider asking in our public groups where community "
                       "members and organizers can help with more context! \n\n In the meantime, You can refer to this guide: https://guide.devfolio.co/")
            else:
                return f"🤔 I couldn't find relevant information for your question in the documentation.\n\n{ORGANIZER_USERNAME} Could you help with this question? \n\n In the meantime, Please refer to this guide: https://guide.devfolio.co/"

        # Generate multiple queries
        prompt_template = ChatPromptTemplate.from_template(QUERY_GENERATION_TEMPLATE)
        prompt = prompt_template.format(original_query=query_text)
        
        model = ChatOpenAI(model="gpt-4.1", temperature=0.3)
        response = model.invoke(prompt).content
        
        # Parse queries
        queries = []
        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                query = line.split('.', 1)[-1].strip().lstrip('•-').strip()
                if query and len(query) > 3:
                    queries.append(query)
                if len(queries) >= 3:
                    break
        
        # Always include original query
        if query_text not in queries:
            queries.insert(0, query_text)
        
        # Search with all queries
        all_results = []
        seen_content = set()
        
        for query in queries:
            results = db.similarity_search_with_relevance_scores(query, k=4)
            for doc, score in results:
                content_hash = hash(doc.page_content[:100])
                if content_hash not in seen_content and score > 0.4:
                    seen_content.add(content_hash)
                    all_results.append((doc, score))
        
        # Sort by relevance score and get only good results
        all_results.sort(key=lambda x: x[1], reverse=True)
        good_results = [(doc, score) for doc, score in all_results if score > 0.5]
        
        if not good_results:
            if is_private:
                return ("🤔 I couldn't find good matches for your question in the documentation.\n\n"
                       "💡 Try asking in our public groups for better assistance! \n\n In the meantime, Please refer to this guide: https://guide.devfolio.co/")
            else:
                return f"🤔 I couldn't find good matches for your question in the documentation. \n\n{ORGANIZER_USERNAME} Could you help with this question? \n\n In the meantime, Please refer to this guide: https://guide.devfolio.co/."

        # Use only top 4 results for context
        results = good_results[:8]
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        
        # Check context length
        if len(context_text) < MIN_CONTEXT_LENGTH:
            if is_private:
                return ("🤔 I found limited information for your question.\n\n"
                       "💡 For more detailed help, consider asking in our public groups!\n\nIn the meantime, Please refer to this guide: https://guide.devfolio.co/")
            else:
                return f"🤔 I found limited information for your question.\n\n{ORGANIZER_USERNAME} This might need human expertise! \n\nIn the meantime, Please refer to this guide: https://guide.devfolio.co/"

        # Evaluate confidence
        confidence_level = evaluate_confidence(query_text, context_text)
        logger.info(f"Confidence level: {confidence_level}")
        
        if confidence_level == 'LOW':
            if is_private:
                return ("🤔 I found some information but I'm not confident enough to provide an accurate answer.\n\n"
                       "💡 For better assistance, try asking this question in our public groups!\n\nIn the meantime, Please refer to this guide: https://guide.devfolio.co/")
            else:
                return f"🤔 I found some information but I'm not confident about the answer.\n\n{ORGANIZER_USERNAME} Could you help with this question? \n\nIn the meantime, Please refer to this guide: https://guide.devfolio.co/"

        # Get AI response
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)
        model = ChatOpenAI(model="gpt-4.1")
        response_text = model.invoke(prompt).content
        
        if "UNCERTAIN" in response_text:
            if is_private:
                return ("🤔 I don't have enough specific information to answer your question confidently.\n\n"
                       "💡 For better assistance, consider asking in our public groups!\n\nIn the meantime, Please refer to this guide: https://guide.devfolio.co/")
            else:
                return f"🤔 I don't have enough specific information to answer your question confidently.\n\n{ORGANIZER_USERNAME} Could you help with one?\n\nIn the meantime, Please refer to this guide: https://guide.devfolio.co/"  
        # Handle partial confidence
        confidence_prefix = ""
        if response_text.startswith("PARTIAL:"):
            response_text = response_text.replace("PARTIAL:", "").strip()
            if confidence_level == 'MEDIUM':
                confidence_prefix = "⚠️ *Partial answer* (some details might be missing):\n\n"

        # Format sources for Telegram
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
        sources_text = "\n".join(unique_sources[:8]) #make the sources unique and limit to 3

        # Add confidence indicator based on context
        confidence_indicator = ""
        if confidence_level == 'MEDIUM':
            if is_private:
                confidence_indicator = "\n\n💡 Need more specific details? Try asking in our public groups!"
            else:
                confidence_indicator = f"\n\n💡 *Need more specific details?* Ask {ORGANIZER_USERNAME} \n\n In the meantime, Please refer to this guide: https://guide.devfolio.co/"

        return f"{confidence_prefix}{response_text}\n\n**📚 Refer these helpful docs for more details**:\n{sources_text}{confidence_indicator}"

    except Exception as e:
        logger.error(f"RAG query error: {e}")
        if is_private:
            return ("❌ Sorry, I encountered an error while processing your question.\n\n"
                   "Please try again later or ask in our public groups for assistance!")
        else:
            return f"❌ Sorry, I encountered an error while processing your question.\n\n{ORGANIZER_USERNAME} Could you help with this technical issue?"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    user = update.effective_user
    message_text = update.message.text
    chat_type = update.effective_chat.type
    is_private = chat_type == 'private'
    
    # Get bot info
    bot_username = context.bot.username
    
    # Log the message
    logger.info(f"Message from {user.first_name} in {chat_type}: {message_text}")
    
    # In groups, only respond if bot is mentioned
    if not is_private:
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
        if is_private:
            response = (
                f"Hello {user.first_name}! 👋\n\n"
                "I'm here to help with your Devfolio and hackathon questions. What would you like to know?\n"
                "💡 Pro tip: You can also ask in our public groups for community support!"
            )
        else:
            response = f"Hello {user.first_name}! Ask me anything about hackathons, Devfolio, or project development!"
        await update.message.reply_text(response)
        return
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Query RAG system with context awareness
    logger.info(f"Querying RAG system with: {message_text}")
    response = query_rag_system(message_text, is_private=is_private)
    
    # Log to webhook
    user_data = {
        "name": f"{user.first_name} {user.last_name if user.last_name else ''} (@{user.username})" if user.username else str(user.id),
        "id": user.id
    }
    
    metadata = {
        "chat_type": chat_type,
        "chat_title": update.effective_chat.title if update.effective_chat.title else None
    }
    
    await log_interaction(
        platform="telegram",
        user_data=user_data,
        query=message_text,
        response=response,
        metadata=metadata
    )
    
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
    logger.info("Starting RAG-integrated test bot...")
    print("🤖 RAG-integrated Telegram bot (Test Version) is starting...")
    print("📋 Bot behavior:")
    print("   • Responds in both private messages and groups")
    print("   • Group messages: Responds when mentioned (@botname)")
    print("   • Private messages: Direct responses with suggestions for public groups")
    print("   • Searches Devfolio documentation for answers")
    print("   • Provides clickable source links")
    print("   • Context-aware responses:")
    print("     - Groups: Tags organizer when uncertain")
    print("     - DMs: Suggests asking in public groups")
    print("   • Uses confidence evaluation to avoid wrong answers")
    print("\n✅ Bot is ready for testing!")
    print("🔗 Try in private chat or add to a group")
    print("   Group example: '@yourbotname How do I organize a hackathon?'")
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
