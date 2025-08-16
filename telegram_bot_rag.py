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
CHROMA_PATH_BOOKS = "chroma"      # Books database

PROMPT_TEMPLATE = """
Answer the question based only on the following context about hackathons and Devfolio platform:

{context}

---

Answer the question based on the above context: {question}

If the context doesn't contain enough information to answer the question, say "I don't have enough information in the provided documentation to answer that question. Could you try rephrasing or asking about hackathon organization, Devfolio features, or application processes?"
"""

def query_rag_system(query_text: str, use_docs: bool = True) -> str:
    """Query the RAG system and return formatted response with sources."""
    try:
        # Choose database
        chroma_path = CHROMA_PATH_DOCS if use_docs else CHROMA_PATH_BOOKS
        
        # Prepare the DB
        embedding_function = OpenAIEmbeddings()
        db = Chroma(persist_directory=chroma_path, embedding_function=embedding_function)

        # Search the DB
        results = db.similarity_search_with_relevance_scores(query_text, k=4)
        if len(results) == 0 or results[0][1] < 0.5:
            return "I couldn't find relevant information for your question. Try asking about hackathon organization, Devfolio features, or application processes."

        # Prepare context and query
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)

        # Get AI response
        model = ChatOpenAI()
        response_text = model.invoke(prompt).content

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
            
            return f"{response_text}\n\n📚 *Sources:*\n{sources_text}"
        else:
            return response_text

    except Exception as e:
        logger.error(f"RAG query error: {e}")
        return "Sorry, I encountered an error while processing your question. Please try again."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    user = update.effective_user
    message_text = update.message.text
    chat_type = update.effective_chat.type
    
    # Get bot info
    bot_username = context.bot.username
    
    # Log the message
    logger.info(f"Message from {user.first_name} in {chat_type}: {message_text}")
    
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
    print("   • In private chats: Responds to all messages with RAG")
    print("   • In groups: Only responds when mentioned (@botname)")
    print("   • Searches Devfolio documentation for answers")
    print("   • Provides clickable source links")
    print("\n🔗 Add the bot to a private group and mention it to test!")
    print("   Example: '@yourbotname How do I organize a hackathon?'")
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
