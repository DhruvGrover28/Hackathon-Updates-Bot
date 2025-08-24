import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError, RetryAfter
from typing import List, Dict, Optional
import time
from datetime import datetime
from database import Database


class TelegramBot:
    """Telegram bot for posting hackathon updates to channels."""
    
    def __init__(self, token: str, channel_id: str, db: Database, rate_limit: int = 30):
        self.bot = Bot(token=token)
        self.channel_id = channel_id
        self.db = db
        self.rate_limit = rate_limit  # messages per minute
        self.last_message_time = 0
        self.message_count = 0
        self.start_time = time.time()
    
    def format_hackathon_message(self, hackathon: Dict) -> str:
        """Format hackathon data into a Telegram message."""
        title = hackathon.get('title', 'Hackathon')
        url = hackathon.get('url', '')
        date_info = hackathon.get('date_info', '')
        description = hackathon.get('description', '')
        
        # Clean up the title
        title = title.strip()
        if len(title) > 100:
            title = title[:97] + "..."
        
        # Format the message
        message = f"🚀 *{title}*\n\n"
        
        if date_info:
            # Clean up date info
            date_info = date_info.strip()
            if date_info:
                message += f"📅 *Date:* {date_info}\n\n"
        
        if description and len(description.strip()) > 0:
            # Clean up description
            description = description.strip()
            if len(description) > 200:
                description = description[:197] + "..."
            message += f"📝 {description}\n\n"
        
        message += f"🔗 [Register Here]({url})\n\n"
        message += "#Hackathon #Competition #Tech #Coding"
        
        return message
    
    def check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.start_time >= 60:
            self.message_count = 0
            self.start_time = current_time
        
        # Check if we've exceeded the rate limit
        if self.message_count >= self.rate_limit:
            return False
        
        return True
    
    def wait_for_rate_limit(self) -> None:
        """Wait if rate limit is exceeded."""
        if not self.check_rate_limit():
            wait_time = 60 - (time.time() - self.start_time)
            if wait_time > 0:
                logging.info(f"Rate limit reached, waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                self.message_count = 0
                self.start_time = time.time()
    
    async def send_message(self, message: str, retries: int = 3) -> bool:
        """Send a message to the Telegram channel with retry logic."""
        for attempt in range(retries):
            try:
                # Check rate limits
                self.wait_for_rate_limit()
                
                # Send the message
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=message,
                    parse_mode='Markdown',
                    disable_web_page_preview=False
                )
                
                self.message_count += 1
                self.last_message_time = time.time()
                
                logging.info("Message sent successfully")
                return True
                
            except RetryAfter as e:
                wait_time = e.retry_after + 1
                logging.warning(f"Rate limited by Telegram, waiting {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                
            except TelegramError as e:
                logging.error(f"Telegram error (attempt {attempt + 1}): {e}")
                if attempt == retries - 1:
                    return False
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                logging.error(f"Unexpected error sending message (attempt {attempt + 1}): {e}")
                if attempt == retries - 1:
                    return False
                await asyncio.sleep(2 ** attempt)
        
        return False
    
    async def test_connection(self) -> bool:
        """Test the bot connection and permissions."""
        try:
            # Get bot info
            bot_info = await self.bot.get_me()
            logging.info(f"Bot connected successfully: @{bot_info.username}")
            
            # Test sending a message
            test_message = "🤖 Hackathon Bot Test - Connection Successful!"
            success = await self.send_message(test_message)
            
            if success:
                logging.info("Test message sent successfully")
                return True
            else:
                logging.error("Failed to send test message")
                return False
                
        except Exception as e:
            logging.error(f"Bot connection test failed: {e}")
            return False
    
    async def post_hackathons(self, max_posts: int = 5) -> Dict:
        """Post unposted hackathons to the channel."""
        logging.info("Starting to post hackathons...")
        
        unposted_hackathons = self.db.get_unposted_hackathons()
        
        if not unposted_hackathons:
            logging.info("No new hackathons to post")
            return {"posted": 0, "failed": 0, "total": 0}
        
        posted_count = 0
        failed_count = 0
        total_count = min(len(unposted_hackathons), max_posts)
        
        for i, hackathon in enumerate(unposted_hackathons[:max_posts]):
            try:
                logging.info(f"Posting hackathon {i+1}/{total_count}: {hackathon['title']}")
                
                message = self.format_hackathon_message(hackathon)
                success = await self.send_message(message)
                
                if success:
                    self.db.mark_as_posted(hackathon['id'])
                    posted_count += 1
                    logging.info(f"Successfully posted: {hackathon['title']}")
                    
                    # Add delay between posts to be respectful
                    if i < total_count - 1:  # Don't wait after the last post
                        await asyncio.sleep(2)
                else:
                    failed_count += 1
                    logging.error(f"Failed to post: {hackathon['title']}")
                
            except Exception as e:
                failed_count += 1
                logging.error(f"Error posting hackathon {hackathon['title']}: {e}")
        
        result = {
            "posted": posted_count,
            "failed": failed_count,
            "total": total_count
        }
        
        logging.info(f"Posting completed: {posted_count} posted, {failed_count} failed, {total_count} total")
        return result
    
    async def send_status_update(self) -> bool:
        """Send a status update with bot statistics."""
        try:
            stats = self.db.get_stats()
            
            message = f"📊 *Hackathon Bot Status Update*\n\n"
            message += f"📈 *Total Hackathons:* {stats.get('total_hackathons', 0)}\n"
            message += f"✅ *Posted:* {stats.get('posted_hackathons', 0)}\n"
            message += f"⏳ *Pending:* {stats.get('pending_hackathons', 0)}\n\n"
            
            if stats.get('recent_sessions'):
                message += f"🕐 *Recent Activity:*\n"
                for session in stats['recent_sessions'][:3]:
                    scraped_at, found, new = session
                    message += f"• {scraped_at}: {found} found, {new} new\n"
            
            message += f"\n🤖 Bot running smoothly! 🚀"
            
            return await self.send_message(message)
            
        except Exception as e:
            logging.error(f"Error sending status update: {e}")
            return False
