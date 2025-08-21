#!/usr/bin/env python3
"""
Discord Bot with RAG Integration
This version integrates with your RAG system and only responds when mentioned in servers.
"""

import logging
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
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
# Discord mention format for organizer - replace YOUR_USER_ID with actual Discord user ID
# To get your user ID: Enable Developer Mode in Discord Settings > Advanced > Developer Mode
# Then right-click your username and select "Copy User ID"
ORGANIZER_USERNAME = "<@845015423207473152>"  # Replace YOUR_USER_ID with actual Discord user ID

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
1. Start with a friendly greeting
2. Provide a short paraphrased answer (1-2 sentences)
3. Break down the solution into clear steps using "**Steps:**" heading
4. Use numbered steps (1., 2., 3., etc.)
6. Do not put title like-> a short answer: and give solution. 
7. Understand the users POV ( how a human would like to read through the help message)

EXAMPLE FORMAT:
Hi Builder! 👋 

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
                confidence_prefix = "⚠️ **Partial answer** (some details might be missing):\n\n"

        # Format sources for Discord
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
            sources_text = "\n".join(unique_sources[:3])  # Limit to 3 sources for Discord
            
            # Add confidence indicator
            confidence_indicator = ""
            if confidence_level == 'MEDIUM':
                confidence_indicator = f"\n\n💡 **Need more specific details?** Ask {ORGANIZER_USERNAME}"

            return f"{confidence_prefix}{response_text}\n\n**Refer documentation for more details**\n{sources_text}{confidence_indicator}"
        else:
            return f"{confidence_prefix}{response_text}"

    except Exception as e:
        logger.error(f"RAG query error: {e}")
        return f"❌ Sorry, I encountered an error while processing your question.\n\n{ORGANIZER_USERNAME} Could you help with this technical issue?"

# Set up Discord bot with intents (without privileged intents)
intents = discord.Intents.default()
# Note: message_content intent is privileged - enable in Discord Developer Portal
# or use slash commands instead for production bots
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Event triggered when bot is ready."""
    logger.info(f"Discord RAG bot logged in as {bot.user}")
    print("🤖 Discord RAG-integrated bot is starting...")
    print("📋 Bot behavior:")
    print("   • Servers ONLY: Responds when mentioned (@botname) in Discord servers")
    print("   • No DMs: Ignores direct messages")
    print("   • Searches Devfolio documentation for answers")
    print("   • Provides clickable source links")
    print("   • Tags organizer when uncertain")
    print("   • Uses confidence evaluation to avoid wrong answers")
    print(f"\n✅ {bot.user} is now online and ready!")
    print("🔗 Add the bot to a server and mention it to test!")
    print(f"   Example: '@{bot.user.display_name} How do I organize a hackathon?'")
    print(f"\n💡 To set up organizer tagging, use command: !myid")
    print("   Then replace YOUR_USER_ID in the bot code with your actual Discord user ID")

@bot.event
async def on_message(message):
    """Handle incoming messages."""
    # Ignore messages from bots
    if message.author == bot.user or message.author.bot:
        return
    
    # Process commands first (for !myid command)
    if message.content.startswith('!'):
        await bot.process_commands(message)
        return
    
    # Only respond in servers (guilds), ignore DMs
    if message.guild is None:
        logger.info(f"Ignoring DM from {message.author}")
        await message.channel.send(
            "👋 Hi! I only work in Discord servers to help with hackathon questions.\n\n"
            "💡 It's always recommended to ask questions in public channels — it helps others who might have the same question and keeps the conversation more engaging.\n\n"
            "🙌 And if you ever get stuck, someone from our team will be happy to jump in and help with the context.\n"
            f"Example: @{bot.user.display_name} How do I organize a hackathon?"
        )
        return
    
    # Check if bot is mentioned
    if bot.user not in message.mentions:
        return
    
    # Get the message content without the mention
    content = message.content
    for mention in message.mentions:
        if mention == bot.user:
            content = content.replace(f'<@{mention.id}>', '').replace(f'<@!{mention.id}>', '').strip()
    
    # If no question provided after removing mention
    if not content.strip():
        response = f"Hello {message.author.display_name}! Ask me anything about hackathons, Devfolio, or project development!"
        await message.channel.send(response)
        return
    
    # Show typing indicator
    async with message.channel.typing():
        # Query RAG system
        logger.info(f"Querying RAG system with: {content}")
        response = query_rag_system(content, use_docs=True)
        
        # Log to webhook
        user_data = {
            "name": str(message.author),
            "id": message.author.id
        }
        
        metadata = {
            "server": message.guild.name if message.guild else "DM",
            "channel": message.channel.name if hasattr(message.channel, 'name') else "Direct Message"
        }
        
        await log_interaction(
            platform="discord",
            user_data=user_data,
            query=content,
            response=response,
            metadata=metadata
        )
    
    # Send response (Discord handles markdown automatically)
    try:
        await message.channel.send(response)
    except discord.HTTPException as e:
        logger.error(f"Error sending message: {e}")
        await message.channel.send("❌ Sorry, I encountered an error while sending the response.")

@bot.event
async def on_error(event, *args, **kwargs):
    """Handle errors."""
    logger.error(f"Discord bot error in {event}: {args}")

@bot.command(name='myid')
async def get_user_id(ctx):
    """Get the user's Discord ID for organizer tagging setup."""
    user_id = ctx.author.id
    await ctx.send(f"🆔 Your Discord User ID is: `{user_id}`\n"
                   f"To set up organizer tagging, replace `YOUR_USER_ID` in the bot code with: `{user_id}`\n"
                   f"Full format: `<@{user_id}>`")

def main():
    """Start the Discord bot."""
    # Get bot token from environment
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        logger.error("DISCORD_BOT_TOKEN not found in environment variables!")
        print("\n🚨 ERROR: Please add DISCORD_BOT_TOKEN to your .env file")
        print("📖 Instructions:")
        print("1. Go to https://discord.com/developers/applications")
        print("2. Create a new application and bot")
        print("3. Copy the bot token")
        print("4. Add DISCORD_BOT_TOKEN=your_token_here to .env file")
        return

    # Check if RAG databases exist
    if not os.path.exists(CHROMA_PATH_DOCS):
        print(f"\n⚠️  WARNING: {CHROMA_PATH_DOCS} not found!")
        print("Run 'python create_docs_database.py' first to create the documentation database.")
        return

    # Start the bot
    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("Invalid Discord bot token!")
        print("\n🚨 ERROR: Invalid DISCORD_BOT_TOKEN!")
        print("Please check your token in the .env file.")
    except Exception as e:
        logger.error(f"Error starting Discord bot: {e}")
        print(f"\n❌ Error starting bot: {e}")

if __name__ == '__main__':
    main()
