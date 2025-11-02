#!/usr/bin/env python3
"""
Telegram bot with slash commands for common FAQs.
No RAG needed - provides quick preset answers to common questions.

Commands:
- /start       : Welcome message
- /help        : Show all available commands
- /hackathon   : Info about creating/joining hackathons
- /judging     : Info about judging process
- /submission  : Info about project submissions
- /team        : Info about creating/joining teams
- /prizes      : Info about prizes and rewards
- /support     : How to get additional support
"""

import os
import logging
from dotenv import load_dotenv

from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN not set in .env")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Command responses
RESPONSES = {
    "start": """
👋 **Welcome to Devfolio Support Bot!**

I'm here to help answer common questions about hackathons on Devfolio.

Use /help to see all available commands for quick answers.

For detailed questions, you can contact our support team.
""",
    
    "help": """
📚 **Available Commands:**

/hackathon - Learn about creating and joining hackathons
/judging - Understand the judging process
/submission - How to submit your project
/team - Creating and managing teams
/prizes - Information about prizes
/support - Get additional help

Simply type any command to get instant answers! 🚀
""",
    
    "hackathon": """
🎯 **Hackathons on Devfolio**

**For Participants:**
• Browse hackathons on devfolio.co
• Click "Apply" on any hackathon
• Fill in your application details
• Submit and wait for confirmation

**For Organizers:**
• Sign up as an organizer
• Click "Create Hackathon"
• Fill in event details (dates, venue, etc.)
• Customize application form
• Publish and manage applications

Need more help? Use /support
""",
    
    "judging": """
⚖️ **Judging Process**

**How it works:**
1. Projects are submitted by participants
2. Organizers assign judges to review
3. Judges evaluate based on criteria
4. Scores are calculated automatically
5. Winners are announced

**Judging Modes:**
• **Online Judging** - Remote evaluation
• **Offline Judging** - In-person review
• **Quadratic Voting** - Community-based
• **Organizer Judging** - Direct review

**For Judges:**
Visit your judging dashboard after assignment and score projects based on the criteria.

Questions? Use /support
""",
    
    "submission": """
📤 **Project Submission**

**How to Submit:**
1. Go to your hackathon dashboard
2. Click "Submit Project"
3. Enter project details:
   • Title and tagline
   • Description
   • Tech stack used
   • Demo link/video
   • GitHub repository
4. Add team members if applicable
5. Click "Submit"

**Important:**
• Submit before the deadline
• You can edit until submission closes
• Include a working demo if possible
• Add clear documentation

**Pro Tips:**
✅ Test all links before submitting
✅ Add screenshots/video demos
✅ Explain what makes your project unique

Need help? Use /support
""",
    
    "team": """
👥 **Teams on Devfolio**

**Creating a Team:**
1. Go to hackathon page
2. Click "Create Team"
3. Set team name
4. Share invite code with members

**Joining a Team:**
1. Get invite code from team leader
2. Go to hackathon page
3. Click "Join Team"
4. Enter the invite code

**Team Rules:**
• Max team size varies by hackathon
• All members must be registered
• Only team leader submits project
• All members share the submission

**Managing Teams:**
• Team leader can remove members
• Members can leave anytime
• Changes allowed until submission

Questions? Use /support
""",
    
    "prizes": """
🏆 **Prizes and Rewards**

**Types of Prizes:**
• **Overall Winners** - Top projects
• **Track Prizes** - Category-specific
• **Sponsor Prizes** - From sponsors
• **Community Awards** - Peer-voted

**Claiming Prizes:**
1. Winners announced after judging
2. Organizers contact winners
3. Provide required details
4. Prizes distributed as specified

**Important:**
• Check prize criteria carefully
• Some prizes require specific tech
• Multiple prizes possible per team
• Follow organizer instructions

**Onchain Credentials:**
Some hackathons offer blockchain credentials for achievements!

More info? Use /support
""",
    
    "support": """
💬 **Get Additional Support**

**Need More Help?**

📧 **Email Support:**
support@devfolio.co

🌐 **Visit Help Center:**
devfolio.co/help

💼 **For Organizers:**
Contact your account manager or email partnerships@devfolio.co

📱 **Community:**
Join our Discord/Telegram community for peer support

**Response Time:**
We typically respond within 24-48 hours.

**Before Contacting:**
• Check if your question is answered in /help
• Provide specific details about your issue
• Include screenshots if relevant
• Mention the hackathon name if applicable
"""
}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message."""
    await update.message.reply_text(RESPONSES["start"], parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all available commands."""
    await update.message.reply_text(RESPONSES["help"], parse_mode='Markdown')


async def hackathon_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Info about hackathons."""
    await update.message.reply_text(RESPONSES["hackathon"], parse_mode='Markdown')


async def judging_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Info about judging process."""
    await update.message.reply_text(RESPONSES["judging"], parse_mode='Markdown')


async def submission_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Info about submissions."""
    await update.message.reply_text(RESPONSES["submission"], parse_mode='Markdown')


async def team_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Info about teams."""
    await update.message.reply_text(RESPONSES["team"], parse_mode='Markdown')


async def prizes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Info about prizes."""
    await update.message.reply_text(RESPONSES["prizes"], parse_mode='Markdown')


async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Additional support information."""
    await update.message.reply_text(RESPONSES["support"], parse_mode='Markdown')


async def setup_commands(app):
    """Set up the bot command menu that appears when users type /"""
    commands = [
        BotCommand("start", "Welcome message"),
        BotCommand("help", "Show all commands"),
        BotCommand("hackathon", "Info about hackathons"),
        BotCommand("judging", "Judging process"),
        BotCommand("submission", "How to submit projects"),
        BotCommand("team", "Create/join teams"),
        BotCommand("prizes", "Prize information"),
        BotCommand("support", "Get additional help"),
    ]
    await app.bot.set_my_commands(commands)
    logger.info("✅ Bot command menu set up successfully")


def build_app():
    """Build and configure the Telegram application."""
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("hackathon", hackathon_command))
    app.add_handler(CommandHandler("judging", judging_command))
    app.add_handler(CommandHandler("submission", submission_command))
    app.add_handler(CommandHandler("team", team_command))
    app.add_handler(CommandHandler("prizes", prizes_command))
    app.add_handler(CommandHandler("support", support_command))

    return app


async def post_init(app):
    """Called after the bot is initialized."""
    await setup_commands(app)


def main():
    """Start the bot."""
    app = build_app()
    
    # Set up the command menu
    app.post_init = post_init
    
    logger.info("🤖 Starting Telegram Commands Bot...")
    logger.info("Available commands: /start, /help, /hackathon, /judging, /submission, /team, /prizes, /support")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
