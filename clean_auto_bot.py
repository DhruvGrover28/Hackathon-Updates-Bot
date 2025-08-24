#!/usr/bin/env python3
"""
Clean Auto Hackathon Bot - No emojis, no Unicode issues
"""

import time
import schedule
import subprocess
import logging
import os
from datetime import datetime

# Setup logging without emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_bot.log'),
        logging.StreamHandler()
    ]
)

def run_live_scraping():
    """Run the live scraper"""
    try:
        logging.info("Starting scheduled live scraping...")
        
        # Run live scraper
        python_path = r"C:/Users/grove/telegram-hackathon-bot/.venv/Scripts/python.exe"
        script_path = r"C:/Users/grove/telegram-hackathon-bot/live_scraper.py"
        
        result = subprocess.run([python_path, script_path], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logging.info("Live scraping completed successfully")
            # Check if any hackathons were found
            if "Added" in result.stdout and "hackathons to database" in result.stdout:
                logging.info("New hackathons found and added to database")
        else:
            logging.error(f"Live scraping failed with return code {result.returncode}")
            
    except subprocess.TimeoutExpired:
        logging.error("Live scraping timed out after 5 minutes")
    except Exception as e:
        logging.error(f"Error running live scraping: {e}")

def run_comprehensive_scraping():
    """Run comprehensive scraping (includes more sources)"""
    try:
        logging.info("Starting scheduled comprehensive scraping...")
        
        python_path = r"C:/Users/grove/telegram-hackathon-bot/.venv/Scripts/python.exe"
        script_path = r"C:/Users/grove/telegram-hackathon-bot/comprehensive_scraper.py"
        
        result = subprocess.run([python_path, script_path], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logging.info("Comprehensive scraping completed")
        else:
            logging.error(f"Comprehensive scraping failed with return code {result.returncode}")
            
    except Exception as e:
        logging.error(f"Error running comprehensive scraping: {e}")

def post_unposted():
    """Post any unposted hackathons"""
    try:
        logging.info("Checking for unposted hackathons...")
        
        python_path = r"C:/Users/grove/telegram-hackathon-bot/.venv/Scripts/python.exe"
        script_path = r"C:/Users/grove/telegram-hackathon-bot/simple_poster.py"
        
        result = subprocess.run([python_path, script_path], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logging.info("Posting check completed")
            if "Successfully posted" in result.stdout:
                logging.info("Posted hackathons to Telegram!")
        else:
            logging.error(f"Posting failed with return code {result.returncode}")
            
    except Exception as e:
        logging.error(f"Error posting: {e}")

def main():
    """Main scheduling function"""
    logging.info("Starting Auto Hackathon Bot - No Unicode Issues")
    logging.info("Scheduling:")
    logging.info("  - Live scraping: Every 6 hours")
    logging.info("  - Comprehensive scraping: Daily at 9 AM")
    logging.info("  - Post check: Every 2 hours")
    
    # Schedule jobs
    schedule.every(6).hours.do(run_live_scraping)
    schedule.every().day.at("09:00").do(run_comprehensive_scraping)
    schedule.every(2).hours.do(post_unposted)
    
    # Run initial scraping
    logging.info("Running initial scraping...")
    run_live_scraping()
    post_unposted()
    
    # Keep running
    logging.info("Scheduler started. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logging.info("Auto bot stopped by user")

if __name__ == "__main__":
    main()
