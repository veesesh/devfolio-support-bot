#!/usr/bin/env python3
"""
Shared webhook logger for both Discord and Telegram bots.
Logs all interactions to a Discord channel using webhooks.
"""

import os
import json
import aiohttp
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

async def log_interaction(platform: str, user_data: dict, query: str, response: str, metadata: dict = None):
    """
    Log bot interactions to Discord webhook
    
    Args:
        platform: 'telegram' or 'discord'
        user_data: Dict containing user information
        query: User's original query
        response: Bot's response
        metadata: Additional context (channel, server etc)
    """
    if not WEBHOOK_URL:
        print("Warning: DISCORD_WEBHOOK_URL not set in .env file")
        return
        
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create Discord embed
    embed = {
        "title": f"Support Bot Interaction - {platform.title()}",
        "color": 0x00ff00 if "UNCERTAIN" not in response else 0xffff00,
        "fields": [
            {
                "name": "User",
                "value": f"`{user_data.get('name')} (ID: {user_data.get('id')})`",
                "inline": True
            },
            {
                "name": "Query",
                "value": query[:1024],  # Discord field value limit
                "inline": False
            },
            {
                "name": "Response",
                "value": response[:1024],  # Discord field value limit
                "inline": False
            }
        ],
        "footer": {
            "text": f"Time: {timestamp}"
        }
    }
    
    # Add platform-specific metadata if provided
    if metadata:
        context_str = []
        if platform == 'discord':
            if metadata.get('server'):
                context_str.append(f"Server: {metadata['server']}")
            if metadata.get('channel'):
                context_str.append(f"Channel: {metadata['channel']}")
        elif platform == 'telegram':
            if metadata.get('chat_type'):
                context_str.append(f"Chat Type: {metadata['chat_type']}")
            if metadata.get('chat_title'):
                context_str.append(f"Chat: {metadata['chat_title']}")
        
        if context_str:
            embed["fields"].append({
                "name": "Context",
                "value": " | ".join(context_str),
                "inline": False
            })

    # Add confidence indicator if present in response
    if "UNCERTAIN" in response:
        embed["fields"].append({
            "name": "Confidence",
            "value": "⚠️ Low confidence response",
            "inline": True
        })
    elif "PARTIAL:" in response:
        embed["fields"].append({
            "name": "Confidence",
            "value": "ℹ️ Partial confidence response",
            "inline": True
        })

    # Prepare webhook payload
    payload = {
        "embeds": [embed]
    }

    # Send to webhook
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(WEBHOOK_URL, json=payload) as response:
                if response.status != 204:
                    print(f"Failed to send to webhook: {response.status}")
        except Exception as e:
            print(f"Webhook error: {e}")
