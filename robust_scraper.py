#!/usr/bin/env python3
"""
Robust scraper - Tries Selenium first, falls back to requests gracefully
"""

import requests
from bs4 import BeautifulSoup
import logging
from database import Database
from telegram_bot import TelegramBot
import os
from dotenv import load_dotenv
import time
import re
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class RobustHackathonScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        self.driver = None
        self.selenium_available = False
    
    def try_selenium_setup(self):
        """Try to setup Selenium, return True if successful"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            print("✅ Selenium setup successful - using full scraping")
            self.selenium_available = True
            return True
            
        except Exception as e:
            print(f"❌ Selenium setup failed: {e}")
            print("📦 Falling back to requests-only mode")
            self.selenium_available = False
            return False
    
    def scrape_with_selenium(self):
        """Full Selenium scraping (original functionality)"""
        try:
            # Import and run the original live_scraper logic
            import subprocess
            result = subprocess.run(
                ["python", "live_scraper.py"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("✅ Selenium scraping completed successfully")
                return True
            else:
                print(f"❌ Selenium scraping failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error with Selenium scraping: {e}")
            return False
    
    def scrape_with_requests_fallback(self):
        """Fallback requests-only scraping"""
        all_hackathons = []
        
        try:
            print("🔄 Using requests-only fallback mode...")
            
            # Try a different approach - look for hackathon APIs or RSS feeds
            hackathons = []
            
            # Method 1: Try hackathon aggregator sites
            aggregator_urls = [
                "https://devpost.com/api/hackathons",
                "https://mlh.io/api/hackathons",
                "https://hackalist.org/api/1.0/2024/08.json"
            ]
            
            for url in aggregator_urls:
                try:
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        if 'json' in response.headers.get('content-type', ''):
                            data = response.json()
                            print(f"✅ Found API data from {url}")
                            # Process API data here
                        else:
                            print(f"📄 Got HTML from {url}")
                except Exception as e:
                    print(f"❌ Failed to fetch {url}: {e}")
            
            # Method 2: Scrape known working pages
            try:
                print("🔍 Scraping MLH (Major League Hacking)...")
                response = self.session.get("https://mlh.io/seasons/2024/events", timeout=20)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    events = soup.find_all(['div', 'article'], class_=lambda x: x and 'event' in x.lower())
                    
                    for event in events[:5]:
                        title_elem = event.find(['h2', 'h3', 'a'])
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            if 'hack' in title.lower():
                                link_elem = event.find('a', href=True)
                                link = link_elem['href'] if link_elem else "https://mlh.io"
                                if not link.startswith('http'):
                                    link = f"https://mlh.io{link}"
                                
                                hackathon = {
                                    'title': title,
                                    'link': link,
                                    'deadline': 'Check website',
                                    'source': 'MLH'
                                }
                                hackathons.append(hackathon)
                                print(f"📝 Found: {title}")
                                
            except Exception as e:
                print(f"❌ MLH scraping failed: {e}")
            
            # Method 3: Add some known active hackathons as backup
            if len(hackathons) == 0:
                backup_hackathons = [
                    {
                        'title': 'Check DevPost for Latest Hackathons',
                        'link': 'https://devpost.com/hackathons',
                        'deadline': 'Various',
                        'source': 'DevPost'
                    },
                    {
                        'title': 'MLH Official Hackathons',
                        'link': 'https://mlh.io/events',
                        'deadline': 'Various',
                        'source': 'MLH'
                    },
                    {
                        'title': 'Unstop Hackathon Competitions',
                        'link': 'https://unstop.com/hackathons',
                        'deadline': 'Various',
                        'source': 'Unstop'
                    }
                ]
                hackathons.extend(backup_hackathons)
                print("🔄 Added backup hackathon sources")
            
            return hackathons
            
        except Exception as e:
            print(f"❌ Fallback scraping failed: {e}")
            return []
    
    def run_robust_scraping(self):
        """Run scraping with Selenium first, fallback to requests"""
        try:
            # Try Selenium first
            selenium_success = False
            if self.try_selenium_setup():
                selenium_success = self.scrape_with_selenium()
                if self.driver:
                    self.driver.quit()
            
            # If Selenium failed, use fallback
            if not selenium_success:
                hackathons = self.scrape_with_requests_fallback()
                
                if hackathons:
                    # Save to database
                    db = Database()
                    new_count = 0
                    
                    for hackathon in hackathons:
                        if db.add_hackathon(hackathon):
                            new_count += 1
                    
                    print(f"💾 Added {new_count} new hackathons to database")
                    
                    # Send to Telegram if new hackathons found
                    if new_count > 0:
                        load_dotenv()
                        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
                        channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
                        
                        if bot_token and channel_id:
                            bot = TelegramBot(bot_token)
                            recent_hackathons = db.get_recent_hackathons(limit=new_count)
                            
                            for hackathon in recent_hackathons:
                                message = f"""
🚀 **New Hackathon Alert!**

**{hackathon['title']}**

📅 **Deadline:** {hackathon['deadline']}
🌐 **Source:** {hackathon['source']}
🔗 **Link:** {hackathon['link']}

Join now and start building! 💻
"""
                                success = bot.send_message(channel_id, message)
                                if success:
                                    print(f"📤 Sent notification for: {hackathon['title']}")
                                time.sleep(1)
                        else:
                            print("❌ Telegram credentials not found")
                    else:
                        print("ℹ️ No new hackathons to notify about")
                else:
                    print("❌ No hackathons found in fallback mode")
            else:
                print("✅ Selenium scraping completed successfully")
                    
        except Exception as e:
            print(f"❌ Error in robust scraping: {e}")

def main():
    """Main function for robust scraping"""
    print("🤖 Starting robust hackathon scraping...")
    scraper = RobustHackathonScraper()
    scraper.run_robust_scraping()
    print("✅ Robust scraping completed!")

if __name__ == "__main__":
    main()
