#!/usr/bin/env python3
"""
Render-compatible version with health check endpoint
"""

import time
import schedule
import subprocess
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Load environment variables
load_dotenv()

# Setup logging without emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_bot.log'),
        logging.StreamHandler()
    ]
)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Bot is running!')
        else:
            self.send_response(404)
            self.end_headers()

def start_health_server():
    """Start health check server for Render"""
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logging.info(f"Health check server started on port {port}")
    server.serve_forever()

def run_live_scraping():
    """Run the live scraper"""
    try:
        logging.info("Starting scheduled live scraping...")
        
        # Run live scraper using Python in PATH
        result = subprocess.run(["python", "live_scraper.py"], 
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
        
        result = subprocess.run(["python", "comprehensive_scraper.py"], 
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
        
        result = subprocess.run(["python", "simple_poster.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logging.info("Posting check completed")
        else:
            logging.error(f"Posting failed with return code {result.returncode}")
            
    except Exception as e:
        logging.error(f"Error posting hackathons: {e}")

def main():
    """Main function to run the auto bot"""
    logging.info("Starting Auto Hackathon Bot - No Unicode Issues")
    
    # Start health check server in background thread
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Schedule jobs
    logging.info("Scheduling:")
    logging.info("  - Live scraping: Every 6 hours")
    logging.info("  - Comprehensive scraping: Daily at 9 AM")
    logging.info("  - Post check: Every 2 hours")
    
    # Schedule live scraping every 6 hours
    schedule.every(6).hours.do(run_live_scraping)
    
    # Schedule comprehensive scraping daily at 9 AM
    schedule.every().day.at("09:00").do(run_comprehensive_scraping)
    
    # Schedule posting check every 2 hours
    schedule.every(2).hours.do(post_unposted)
    
    # Run initial scraping
    logging.info("Running initial scraping...")
    run_live_scraping()
    post_unposted()
    
    logging.info("Scheduler started. Press Ctrl+C to stop.")
    
    # Keep the script running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logging.info("Auto bot stopped by user")

if __name__ == "__main__":
    main()
