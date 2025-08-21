#!/usr/bin/env python3
"""
Discord Bot with RAG Integration - Test Version
This version handles both DMs and server messages differently.
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
ORGANIZER_USERNAME = "<@845015423207473152>"  # Replace with actual Discord user ID

# Confidence threshold - lower means more strict
CONFIDENCE_THRESHOLD = 0.65
MIN_CONTEXT_LENGTH = 200  # Minimum context length for confident answers

# Existing prompt templates remain the same
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
        
        model = ChatOpenAI(temperature=0)
        confidence_level = model.invoke(prompt).content.strip().upper()
        
        return confidence_level if confidence_level in ['HIGH', 'MEDIUM', 'LOW'] else 'LOW'
    except Exception as e:
        logger.error(f"Confidence evaluation error: {e}")
        return 'LOW'

def query_rag_system(query_text: str, is_dm: bool = False) -> str:
    """Query the RAG system and return formatted response based on context (DM vs Server)."""
    try:
        # Use documentation database
        chroma_path = CHROMA_PATH_DOCS
        
        # Prepare the DB
        embedding_function = OpenAIEmbeddings()
        db = Chroma(persist_directory=chroma_path, embedding_function=embedding_function)

        # First try with original query to check confidence
        initial_results = db.similarity_search_with_relevance_scores(query_text, k=4)
        
        # Check if we got high confidence results from initial query
        high_confidence_threshold = 0.65
        has_high_confidence = any(score > high_confidence_threshold for _, score in initial_results)
        
        if not has_high_confidence:
            if is_dm:
                return ("🤔 I couldn't find relevant information for your question in the documentation.\n\n"
                       "💡 For better support, consider asking in our public channels where community "
                       "members and organizers can help with more context!")
            else:
                return f"🤔 I couldn't find relevant information for your question in the documentation.\n\n{ORGANIZER_USERNAME} Could you help with this question?"
            
        # Generate multiple queries using the existing logic
        prompt_template = ChatPromptTemplate.from_template(QUERY_GENERATION_TEMPLATE)
        prompt = prompt_template.format(original_query=query_text)
        
        model = ChatOpenAI(temperature=0.3)
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
        
        if query_text not in queries:
            queries.insert(0, query_text)
        
        # Search with all queries
        all_results = []
        seen_content = set()
        
        for query in queries:
            results = db.similarity_search_with_relevance_scores(query, k=3)
            for doc, score in results:
                content_hash = hash(doc.page_content[:100])
                if content_hash not in seen_content and score > 0.4:
                    seen_content.add(content_hash)
                    all_results.append((doc, score))
        
        # Sort and filter results
        all_results.sort(key=lambda x: x[1], reverse=True)
        good_results = [(doc, score) for doc, score in all_results if score > 0.5]
        
        if not good_results:
            if is_dm:
                return ("🤔 I couldn't find good matches for your question in the documentation.\n\n"
                       "💡 Try asking in our public channels for better assistance!")
            else:
                return f"🤔 I couldn't find good matches for your question in the documentation.\n\n{ORGANIZER_USERNAME} Could you help with this question?"
            
        # Use top 4 results
        results = good_results[:4]
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        
        if len(context_text) < MIN_CONTEXT_LENGTH:
            if is_dm:
                return ("🤔 I found limited information for your question.\n\n"
                       "💡 For more detailed help, consider asking in our public channels!")
            else:
                return f"🤔 I found limited information for your question.\n\n{ORGANIZER_USERNAME} This might need human expertise!"
        
        # Evaluate confidence
        confidence_level = evaluate_confidence(query_text, context_text)
        logger.info(f"Confidence level: {confidence_level}")
        
        if confidence_level == 'LOW':
            if is_dm:
                return ("🤔 I found some information but I'm not confident enough to provide an accurate answer.\n\n"
                       "if you ask again in Devfolio group our staff may be able to chime in!")
            else:
                return f"🤔 I found some information but I'm not confident about the answer to avoid giving incorrect details.\n\n{ORGANIZER_USERNAME} Could you help with this question: '{query_text}'?"

        # Get AI response
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)
        model = ChatOpenAI()
        response_text = model.invoke(prompt).content
        
        if "UNCERTAIN" in response_text:
            if is_dm:
                return ("🤔 I don't have enough specific information to answer your question confidently.\n\n"
                       "💡 For better assistance, consider asking in our public channels!")
            else:
                return f"🤔 I don't have enough specific information to answer your question confidently.\n\n{ORGANIZER_USERNAME} Could you help with: '{query_text}'?"
        
        # Handle partial confidence
        confidence_prefix = ""
        if response_text.startswith("PARTIAL:"):
            response_text = response_text.replace("PARTIAL:", "").strip()
            if confidence_level == 'MEDIUM':
                confidence_prefix = "⚠️ **Partial answer** (some details might be missing):\n\n"

        # Format sources
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
        
        unique_sources = list(dict.fromkeys(sources))
        sources_text = "\n".join(unique_sources[:3])

        # Add confidence indicator based on context
        confidence_indicator = ""
        if confidence_level == 'MEDIUM':
            if is_dm:
                confidence_indicator = "\n\n💡 Need more specific details? Try asking in our public channels!"
            else:
                confidence_indicator = f"\n\n💡 **Need more specific details?** Ask {ORGANIZER_USERNAME}"

        return f"{confidence_prefix}{response_text}\n\n**Refer documentation for more details**\n{sources_text}{confidence_indicator}"

    except Exception as e:
        logger.error(f"RAG query error: {e}")
        if is_dm:
            return ("❌ Sorry, I encountered an error while processing your question.\n\n"
                   "Please try again later or ask in our public channels for assistance!")
        else:
            return f"❌ Sorry, I encountered an error while processing your question.\n\n{ORGANIZER_USERNAME} Could you help with this technical issue?"

# Set up Discord bot
intents = discord.Intents.default()
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
    print("   • Responds in both servers and DMs")
    print("   • Server messages: Tags organizer for uncertain answers")
    print("   • DM messages: Suggests public channels for better support")
    print("   • Provides clickable source links")
    print("   • Uses confidence evaluation to avoid wrong answers")
    print(f"\n✅ {bot.user} is now online and ready!")
    print("🔗 Add the bot to a server and mention it to test!")
    print(f"   Example: '@{bot.user.display_name} How do I organize a hackathon?'")
    print(f"\n💡 To set up organizer tagging, use command: !myid")

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
    
    # Different handling for DMs vs server messages
    is_dm = message.guild is None
    
    # In servers, only respond when mentioned
    if not is_dm and bot.user not in message.mentions:
        return
    
    # Get the message content without the mention
    content = message.content
    if bot.user in message.mentions:
        for mention in message.mentions:
            if mention == bot.user:
                content = content.replace(f'<@{mention.id}>', '').replace(f'<@!{mention.id}>', '').strip()
    
    # If no question provided
    if not content.strip():
        if is_dm:
            response = (
                f"Hello {message.author.display_name}! 👋\n\n"
                "I'm here to help with your Devfolio and hackathon questions. What would you like to know?\n"
                "💡 Pro tip: You can also ask in our public channels for community support!"
            )
        else:
            response = f"Hello {message.author.display_name}! Ask me anything about hackathons, Devfolio, or project development!"
        await message.channel.send(response)
        return
    
    # Show typing indicator
    async with message.channel.typing():
        # Query RAG system with context awareness
        logger.info(f"Querying RAG system with: {content}")
        response = query_rag_system(content, is_dm=is_dm)
        
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
    
    # Send response
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

    if not os.path.exists(CHROMA_PATH_DOCS):
        print(f"\n⚠️  WARNING: {CHROMA_PATH_DOCS} not found!")
        print("Run 'python create_docs_database.py' first to create the documentation database.")
        return

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
