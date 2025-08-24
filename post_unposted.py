#!/usr/bin/env python3
"""
Post Unposted Hackathons - Send all pending hackathons to Telegram
"""

import asyncio
import os
from dotenv import load_dotenv
from database import Database
from telegram_bot import TelegramBot

load_dotenv()

async def post_unposted_hackathons():
    """Post all unposted hackathons to Telegram"""
    print("📤 Posting unposted hackathons to Telegram...")
    
    # Initialize components
    db = Database()
    telegram_bot = TelegramBot(
        token=os.getenv("TELEGRAM_BOT_TOKEN"),
        channel_id=os.getenv("TELEGRAM_CHANNEL_ID"),
        db=db
    )
    
    # Get unposted hackathons
    unposted = db.get_unposted_hackathons()
    print(f"Found {len(unposted)} unposted hackathons")
    
    if not unposted:
        print("ℹ️ No hackathons to post")
        return
    
    # Display what we're about to post
    print("\n📋 Hackathons to post:")
    for i, hackathon in enumerate(unposted, 1):
        # hackathon is a dictionary from database
        print(f"{i}. {hackathon['title']}")
    
    # Post them
    try:
        await telegram_bot.post_hackathons(unposted)
        print("✅ Successfully posted all hackathons to Telegram!")
        
        # Check final stats
        stats = db.get_stats()
        print(f"\n📈 FINAL STATS:")
        print(f"  Total hackathons: {stats['total_hackathons']}")
        print(f"  Posted to channel: {stats['posted_hackathons']}")
        print(f"  Pending: {stats['pending_hackathons']}")
        
    except Exception as e:
        print(f"❌ Error posting to Telegram: {e}")

if __name__ == "__main__":
    asyncio.run(post_unposted_hackathons())
