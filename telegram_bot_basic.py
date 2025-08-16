#!/usr/bin/env python3
"""
Basic Telegram Bot - Step 1
This is the most basic version that just echoes messages back.
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
    
    # Log the message
    logger.info(f"Message from {user.first_name}: {message_text}")
    
    # Simple echo response for now
    response = f"Hello {user.first_name}! You said: {message_text}"
    
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
        print("To get a token:")
        print("1. Message @BotFather on Telegram")
        print("2. Send /newbot")
        print("3. Choose a name and username for your bot")
        print("4. Copy the token and add it to .env file")
        return

    # Create the Application
    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Starting bot...")
    print("🤖 Bot is starting...")
    print("Add the bot to a group and send messages to test!")
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
