#!/usr/bin/env python3
"""
Simple Render Bot - Just scraping and posting, no commands
"""

import time
import schedule
import logging
import os
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('render_bot.log'),
        logging.StreamHandler()
    ]
)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for health check"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
        
    def log_message(self, format, *args):
        """Suppress default HTTP logging"""
        pass

def start_health_server():
    """Start health check server on port 10000"""
    try:
        server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
        logging.info("Health check server started on port 10000")
        server.serve_forever()
    except Exception as e:
        logging.error(f"Health server error: {e}")

def start_command_bot():
    """Start Telegram DM command bot in a background thread."""
    try:
        import asyncio
        from telegram import Update
        from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logging.error("Missing TELEGRAM_BOT_TOKEN for command bot")
            return

        async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(
                "Hi! I post hackathon updates to the channel.\n"
                "Commands: /help, /status"
            )

        async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(
                "Commands:\n"
                "/start - welcome message\n"
                "/help - this help\n"
                "/status - basic bot status"
            )

        async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text("Bot is running and posting updates.")

        app = ApplicationBuilder().token(bot_token).build()
        app.add_handler(CommandHandler("start", start_cmd))
        app.add_handler(CommandHandler("help", help_cmd))
        app.add_handler(CommandHandler("status", status_cmd))

        # Ensure the thread has an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        logging.info("Command bot polling started")
        app.run_polling(poll_interval=1, close_loop=True)
    except Exception as e:
        logging.error(f"Command bot error: {e}")

def run_scraping_and_posting():
    """Run scraping and posting directly"""
    try:
        logging.info("Starting scraping and posting cycle...")
        
        # Scrape and post using the unified path (dedupe + posted flags)
        logging.info("Running fast scraper...")
        from fast_scraper import FastHackathonScraper
        from telegram_bot import TelegramBot
        import asyncio

        scraper = FastHackathonScraper()
        hackathons = scraper.scrape_all()
        scraper.close()
        logging.info("Scraping completed")

        if not hackathons:
            logging.info("No hackathons found to post")
            return

        logging.info("Running telegram posting...")
        telegram_bot = TelegramBot()
        result = asyncio.run(telegram_bot.post_hackathons(hackathons))
        logging.info(f"Posting completed: {result}")
        
        logging.info("Scraping and posting cycle completed successfully")
        
    except Exception as e:
        logging.error(f"Cycle failed: {e}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")

def main():
    """Main function - simple scraping every 6 hours"""
    try:
        logging.info("Simple Hackathon Bot starting...")
        
        # Check environment variables
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
        
        if not bot_token or not channel_id:
            logging.error("Missing environment variables!")
            return
            
        logging.info(f"Channel: {channel_id}")
        logging.info("Environment loaded successfully")
        
        # Start health check server
        health_thread = threading.Thread(target=start_health_server, daemon=True)
        health_thread.start()

        # Start command bot for DM commands
        command_thread = threading.Thread(target=start_command_bot, daemon=True)
        command_thread.start()
        
        # Schedule scraping every N hours (default 6)
        interval_hours = int(os.getenv("SCRAPE_INTERVAL_HOURS", "6"))
        schedule.every(interval_hours).hours.do(run_scraping_and_posting)
        logging.info(f"Scheduled scraping every {interval_hours} hours")
        
        # Run initial cycle
        logging.info("Running initial scraping cycle...")
        try:
            run_scraping_and_posting()
            logging.info("Initial cycle completed successfully")
        except Exception as e:
            logging.error(f"Initial cycle failed: {e}")
            logging.info("Will continue with scheduled cycles...")
        
        # Main loop
        logging.info("Bot operational! Running every 6 hours.")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        # Keep alive for health checks
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()
