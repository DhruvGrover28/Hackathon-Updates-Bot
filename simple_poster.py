#!/usr/bin/env python3
"""
Simple Hackathon Poster - Post specific hackathons to Telegram
"""

import asyncio
import os
from dotenv import load_dotenv
from database import Database
from telegram_bot import TelegramBot

load_dotenv()

async def post_all_unposted():
    """Post all unposted hackathons to Telegram"""
    print("Posting unposted hackathons to Telegram...")
    
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
        print("No hackathons to post")
        return
    
    # Display what we're about to post
    print("\nHackathons to post:")
    for i, hackathon in enumerate(unposted, 1):
        print(f"{i}. {hackathon['title']}")
    
    # Post them using the telegram bot's method (it will get them from DB)
    try:
        result = await telegram_bot.post_hackathons(max_posts=len(unposted))
        
        print(f"\nPosting Results:")
        print(f"  Successfully posted: {result['posted']}")
        print(f"  Failed: {result['failed']}")
        print(f"  Total processed: {result['total']}")
        
        # Check final stats
        stats = db.get_stats()
        print(f"\nFINAL STATS:")
        print(f"  Total hackathons: {stats['total_hackathons']}")
        print(f"  Posted to channel: {stats['posted_hackathons']}")
        print(f"  Pending: {stats['pending_hackathons']}")
        
        if result['posted'] > 0:
            print(f"\nSuccessfully posted {result['posted']} hackathons to your Telegram channel!")
            print(f"Check @joinhackathonupdates to see them!")
        
    except Exception as e:
        print(f"Error posting to Telegram: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(post_all_unposted())
