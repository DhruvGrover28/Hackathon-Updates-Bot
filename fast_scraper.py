#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fast Hackathon Scraper - Optimized version for quick results
"""

import requests
from bs4 import BeautifulSoup
import logging
from database import Database
import os
from dotenv import load_dotenv
import time

# Try to import Selenium components
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    By = None

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class FastHackathonScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        })
        self.driver = None
        self.selenium_available = False
    
    def setup_selenium(self):
        """Quick Selenium setup"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1280,720")
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.selenium_available = True
            print("✅ Selenium ready")
            return True
        except Exception as e:
            print(f"❌ Selenium failed: {e}")
            return False
    
    def scrape_devpost_fast(self):
        """Fast DevPost scraping - focus on what works"""
        hackathons = []
        try:
            print("🔍 DevPost scraping...")
            self.driver.get("https://devpost.com/hackathons")
            time.sleep(2)
            
            # Get hackathon tiles (this was working)
            tiles = self.driver.find_elements(By.CSS_SELECTOR, ".hackathon-tile")
            print(f"Found {len(tiles)} hackathon tiles")
            
            for tile in tiles[:5]:  # Process only first 5
                try:
                    # Get title from h3 (this was working)
                    title_elem = tile.find_element(By.CSS_SELECTOR, "h3")
                    title = title_elem.text.strip()
                    
                    if len(title) < 8:
                        continue
                    
                    # Get URL
                    link_elem = tile.find_element(By.CSS_SELECTOR, "a")
                    url = link_elem.get_attribute('href')
                    
                    if url and 'devpost.com' in url:
                        hackathons.append({
                            'title': title,
                            'url': url,
                            'source': 'DevPost',
                            'date_info': 'Check DevPost for dates',
                            'description': f'🚀 {title}\nDevPost\n📅 Date: Check DevPost for dates\n📝 Live from DevPost.com\n🔗 {url}\n#Hackathon #Competition #Tech #Coding'
                        })
                        print(f"✅ Found: {title}")
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"DevPost error: {e}")
        
        return hackathons
    
    def scrape_mlh_fast(self):
        """Fast MLH scraping"""
        hackathons = []
        try:
            print("🔍 MLH scraping...")
            self.driver.get("https://mlh.io/events")
            time.sleep(2)
            
            # Look for event elements
            events = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='event'], a[href*='event']")
            print(f"Found {len(events)} potential events")
            
            for event in events[:5]:
                try:
                    title = event.text.strip()
                    if len(title) < 8 or len(title) > 100:
                        continue
                    
                    # Must have hackathon indicators
                    if not any(word in title.lower() for word in ['hack', 'thon', '2024', '2025']):
                        continue
                    
                    # Skip generic terms
                    if any(word in title.lower() for word in ['events', 'mlh', 'browse']):
                        continue
                    
                    url = ""
                    try:
                        url = event.get_attribute('href')
                    except:
                        pass
                    
                    if not url:
                        try:
                            link = event.find_element(By.CSS_SELECTOR, "a")
                            url = link.get_attribute('href')
                        except:
                            continue
                    
                    if url and not url.startswith('http'):
                        url = f"https://mlh.io{url}"
                    
                    if url:
                        hackathons.append({
                            'title': title,
                            'url': url,
                            'source': 'MLH',
                            'date_info': 'Check MLH for dates',
                            'description': f'🚀 {title}\nMLH\n📅 Date: Check MLH for dates\n📝 Live from MLH.io\n🔗 {url}\n#Hackathon #Competition #Tech #Coding'
                        })
                        print(f"✅ Found: {title}")
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"MLH error: {e}")
        
        return hackathons
    
    def send_telegram_notifications(self, hackathons):
        """Send hackathons to Telegram"""
        load_dotenv()
        
        BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        CHAT_ID = os.getenv('TELEGRAM_CHANNEL_ID')  # Changed from TELEGRAM_CHAT_ID
        
        if not BOT_TOKEN or not CHAT_ID:
            print("❌ Missing Telegram credentials")
            return
        
        print(f"📤 Sending {len(hackathons)} notifications...")
        
        for hackathon in hackathons:
            try:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                data = {
                    'chat_id': CHAT_ID,
                    'text': hackathon['description'],
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': False
                }
                
                response = requests.post(url, data=data, timeout=10)
                if response.status_code == 200:
                    print(f"✅ Sent: {hackathon['title']}")
                else:
                    print(f"❌ Failed to send: {hackathon['title']}")
                    
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error sending {hackathon['title']}: {e}")
    
    def run(self):
        """Main scraping function"""
        print("🤖 Fast hackathon scraping started...")
        
        if not self.setup_selenium():
            print("❌ Cannot run without Selenium")
            return
        
        all_hackathons = []
        
        # Scrape DevPost (this was working well)
        devpost_hackathons = self.scrape_devpost_fast()
        all_hackathons.extend(devpost_hackathons)
        
        # Scrape MLH
        mlh_hackathons = self.scrape_mlh_fast()
        all_hackathons.extend(mlh_hackathons)
        
        if self.driver:
            self.driver.quit()
        
        print(f"✅ Found {len(all_hackathons)} total hackathons")
        
        if all_hackathons:
            # Add to database
            db = Database()
            added_count = 0
            for hackathon in all_hackathons:
                if db.add_hackathon(hackathon['title'], hackathon['url'], hackathon['date_info'], hackathon['description']):
                    added_count += 1
            
            print(f"💾 Added {added_count} new hackathons to database")
            
            # Send notifications
            self.send_telegram_notifications(all_hackathons)
        else:
            print("❌ No hackathons found")
        
        print("✅ Fast scraping completed!")

if __name__ == "__main__":
    scraper = FastHackathonScraper()
    scraper.run()
