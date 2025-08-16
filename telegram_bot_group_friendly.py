#!/usr/bin/env python3
"""
Telegram Bot - Step 2: Group-Friendly Version
This version only responds when the bot is mentioned in groups.
"""

import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
        # Check if bot is mentioned
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
    
    # Respond to the message
    if message_text.strip():
        response = f"Hello {user.first_name}! You asked: {message_text}\n\n(This is just a test response. RAG integration coming next!)"
    else:
        response = f"Hello {user.first_name}! How can I help you?"
    
    await update.message.reply_text(response)

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

    # Create the Application
    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Starting group-friendly bot...")
    print("🤖 Group-friendly bot is starting...")
    print("📋 Bot behavior:")
    print("   • In private chats: Responds to all messages")
    print("   • In groups: Only responds when mentioned (@botname)")
    print("   • Add the bot to a private group and mention it to test!")
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
