#!/usr/bin/env python3
"""
Aggressive live data scraper for Unstop, DevPost, and Devfolio
Uses multiple techniques: requests, selenium, and API attempts
"""

import asyncio
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
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class LiveHackathonScraper:
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
    
    def setup_selenium_driver(self):
        """Setup Chrome driver with optimized settings"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            # Suppress Chrome internal errors
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-background-networking")
            chrome_options.add_argument("--disable-sync")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--log-level=3")  # Suppress INFO, WARNING, ERROR
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            print("Chrome driver setup successful")
            return driver
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            return None
    
    def scrape_unstop_live(self):
        """Scrape live data from Unstop.com"""
        hackathons = []
        
        try:
            print("Scraping Unstop.com...")
            
            # Method 1: Direct requests
            url = "https://unstop.com/hackathons"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for various hackathon selectors
                selectors = [
                    'a[href*="/hackathons/"]',
                    '.card a[href*="hackathon"]',
                    '.competition-card',
                    '.hackathon-card',
                    '[data-testid*="hackathon"]',
                    '.event-card',
                    '.listing-item'
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    if elements:
                        print(f"Found {len(elements)} elements with selector: {selector}")
                        
                        for element in elements[:10]:  # Limit to avoid spam
                            title = ""
                            url_href = ""
                            
                            # Extract title
                            if element.get_text(strip=True):
                                title = element.get_text(strip=True)
                            elif element.find(['h1', 'h2', 'h3', 'h4', 'h5']):
                                title = element.find(['h1', 'h2', 'h3', 'h4', 'h5']).get_text(strip=True)
                            
                            # Extract URL
                            if element.get('href'):
                                url_href = element.get('href')
                                if url_href.startswith('/'):
                                    url_href = f"https://unstop.com{url_href}"
                            elif element.find('a'):
                                url_href = element.find('a').get('href', '')
                                if url_href.startswith('/'):
                                    url_href = f"https://unstop.com{url_href}"
                            
                            if title and url_href and len(title) > 5:
                                hackathons.append({
                                    'title': title[:100],  # Limit title length
                                    'url': url_href,
                                    'date_info': 'Check Unstop for dates',
                                    'description': 'Live from Unstop.com'
                                })
                        
                        if hackathons:
                            break  # Found hackathons, no need to try other selectors
                
                print(f"Unstop.com: Found {len(hackathons)} hackathons via requests")
                
            # Method 2: Try with Selenium if requests didn't work well
            if len(hackathons) < 3:
                print("Trying Unstop.com with Selenium...")
                self.driver = self.setup_selenium_driver()
                
                if self.driver:
                    try:
                        self.driver.get("https://unstop.com/hackathons")
                        time.sleep(5)  # Wait for page to load
                        
                        # Try to find hackathon elements
                        hackathon_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='hackathon']")
                        
                        for link in hackathon_links[:5]:
                            try:
                                title = link.text.strip()
                                href = link.get_attribute('href')
                                
                                if title and href and len(title) > 5:
                                    hackathons.append({
                                        'title': title[:100],
                                        'url': href,
                                        'date_info': 'Check Unstop for dates',
                                        'description': 'Live from Unstop.com (Selenium)'
                                    })
                            except Exception:
                                continue
                        
                        print(f"Unstop.com Selenium: Found {len(hackathons)} total hackathons")
                        
                    except Exception as e:
                        print(f"Selenium error for Unstop: {e}")
                    finally:
                        if self.driver:
                            self.driver.quit()
                            self.driver = None
                            
        except Exception as e:
            print(f"Error scraping Unstop: {e}")
        
        return hackathons
    
    def scrape_devpost_live(self):
        """Scrape live data from DevPost.com"""
        hackathons = []
        
        try:
            print("Scraping DevPost.com...")
            
            urls_to_try = [
                "https://devpost.com/hackathons",
                "https://devpost.com/hackathons/open",
                "https://devpost.com/hackathons/upcoming"
            ]
            
            for url in urls_to_try:
                try:
                    response = self.session.get(url, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # DevPost specific selectors
                        selectors = [
                            '.hackathon-tile',
                            '.challenge-tile',
                            '.featured-hackathon',
                            'article.hackathon',
                            '.hackathon-card',
                            'a[href*="/challenges/"]',
                            '.software-entry'
                        ]
                        
                        for selector in selectors:
                            elements = soup.select(selector)
                            if elements:
                                print(f"DevPost: Found {len(elements)} elements with selector: {selector}")
                                
                                for element in elements[:8]:
                                    title = ""
                                    url_href = ""
                                    date_info = ""
                                    
                                    # Extract title
                                    title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'h5']) or element.find(class_=re.compile(r'title|name'))
                                    if title_elem:
                                        title = title_elem.get_text(strip=True)
                                    elif element.get_text(strip=True):
                                        title = element.get_text(strip=True)
                                    
                                    # Extract URL
                                    if element.name == 'a' and element.get('href'):
                                        url_href = element.get('href')
                                    elif element.find('a'):
                                        url_href = element.find('a').get('href', '')
                                    
                                    if url_href and not url_href.startswith('http'):
                                        url_href = f"https://devpost.com{url_href}"
                                    
                                    # Extract date if available
                                    date_elem = element.find(class_=re.compile(r'date|time|deadline'))
                                    if date_elem:
                                        date_info = date_elem.get_text(strip=True)
                                    
                                    if title and url_href and len(title) > 5:
                                        hackathons.append({
                                            'title': title[:100],
                                            'url': url_href,
                                            'date_info': date_info or 'Check DevPost for dates',
                                            'description': 'Live from DevPost.com'
                                        })
                                
                                if hackathons:
                                    break
                        
                        if hackathons:
                            break  # Found hackathons, stop trying other URLs
                            
                except Exception as e:
                    print(f"Error with DevPost URL {url}: {e}")
                    continue
            
            print(f"DevPost.com: Found {len(hackathons)} hackathons")
            
        except Exception as e:
            print(f"Error scraping DevPost: {e}")
        
        return hackathons
    
    def scrape_devfolio_live(self):
        """Scrape live data from Devfolio.co"""
        hackathons = []
        
        try:
            print("Scraping Devfolio.co...")
            
            urls_to_try = [
                "https://devfolio.co/hackathons",
                "https://devfolio.co/discover",
                "https://devfolio.co/events"
            ]
            
            for url in urls_to_try:
                try:
                    response = self.session.get(url, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Devfolio specific selectors
                        selectors = [
                            '.hackathon-card',
                            '.event-card',
                            '.challenge-card',
                            'a[href*="/hackathons/"]',
                            '.hackathon-tile',
                            '[data-testid*="hackathon"]',
                            '.card'
                        ]
                        
                        for selector in selectors:
                            elements = soup.select(selector)
                            if elements:
                                print(f"Devfolio: Found {len(elements)} elements with selector: {selector}")
                                
                                for element in elements[:8]:
                                    title = ""
                                    url_href = ""
                                    date_info = ""
                                    
                                    # Extract title
                                    title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'h5']) or element.find(class_=re.compile(r'title|name'))
                                    if title_elem:
                                        title = title_elem.get_text(strip=True)
                                    elif element.get_text(strip=True):
                                        title = element.get_text(strip=True)
                                    
                                    # Extract URL
                                    if element.name == 'a' and element.get('href'):
                                        url_href = element.get('href')
                                    elif element.find('a'):
                                        url_href = element.find('a').get('href', '')
                                    
                                    if url_href and not url_href.startswith('http'):
                                        url_href = f"https://devfolio.co{url_href}"
                                    
                                    # Extract date if available
                                    date_elem = element.find(class_=re.compile(r'date|time|deadline'))
                                    if date_elem:
                                        date_info = date_elem.get_text(strip=True)
                                    
                                    if title and url_href and len(title) > 5:
                                        hackathons.append({
                                            'title': title[:100],
                                            'url': url_href,
                                            'date_info': date_info or 'Check Devfolio for dates',
                                            'description': 'Live from Devfolio.co'
                                        })
                                
                                if hackathons:
                                    break
                        
                        if hackathons:
                            break
                            
                except Exception as e:
                    print(f"Error with Devfolio URL {url}: {e}")
                    continue
            
            print(f"Devfolio.co: Found {len(hackathons)} hackathons")
            
        except Exception as e:
            print(f"Error scraping Devfolio: {e}")
        
        return hackathons

async def main():
    print("Starting aggressive live scraping from Unstop, DevPost, and Devfolio...")
    
    # Load environment
    load_dotenv()
    
    # Initialize database
    db = Database()
    
    # Initialize scraper
    scraper = LiveHackathonScraper()
    
    all_hackathons = []
    
    # Scrape all three sites
    print("\n" + "="*60)
    unstop_hackathons = scraper.scrape_unstop_live()
    all_hackathons.extend(unstop_hackathons)
    
    print("\n" + "="*60)
    devpost_hackathons = scraper.scrape_devpost_live()
    all_hackathons.extend(devpost_hackathons)
    
    print("\n" + "="*60)
    devfolio_hackathons = scraper.scrape_devfolio_live()
    all_hackathons.extend(devfolio_hackathons)
    
    print("\n" + "="*60)
    print(f"TOTAL LIVE SCRAPED RESULTS:")
    print(f"  Unstop.com: {len(unstop_hackathons)} hackathons")
    print(f"  DevPost.com: {len(devpost_hackathons)} hackathons")
    print(f"  Devfolio.co: {len(devfolio_hackathons)} hackathons")
    print(f"  TOTAL: {len(all_hackathons)} hackathons")
    
    # Remove duplicates by URL
    seen_urls = set()
    unique_hackathons = []
    for hackathon in all_hackathons:
        if hackathon['url'] not in seen_urls:
            seen_urls.add(hackathon['url'])
            unique_hackathons.append(hackathon)
    
    print(f"Unique hackathons after deduplication: {len(unique_hackathons)}")
    
    if unique_hackathons:
        # Add to database (limit to 8 to avoid spam)
        new_count = 0
        for hackathon in unique_hackathons[:8]:
            if db.add_hackathon(
                hackathon['title'],
                hackathon['url'],
                hackathon['date_info'],
                hackathon['description']
            ):
                new_count += 1
                print(f"  Added: {hackathon['title']}")
            else:
                print(f"  Already exists: {hackathon['title']}")
        
        print(f"\nAdded {new_count} new live hackathons to database")
        
        if new_count > 0:
            # Post to Telegram
            telegram_bot = TelegramBot(
                token=os.getenv('TELEGRAM_BOT_TOKEN'),
                channel_id=os.getenv('TELEGRAM_CHANNEL_ID'),
                db=db
            )
            
            print("Posting live hackathons to Telegram channel...")
            results = await telegram_bot.post_hackathons(max_posts=new_count)
            
            print(f"\nPOSTING RESULTS:")
            print(f"  Posted: {results['posted']}")
            print(f"  Failed: {results['failed']}")
            print(f"  Total: {results['total']}")
            
            if results['posted'] > 0:
                print(f"\nSuccessfully posted {results['posted']} LIVE hackathons!")
                print("Check your Telegram channel @joinhackathonupdates!")
                
                print(f"\nLIVE hackathons posted:")
                for i, h in enumerate(unique_hackathons[:results['posted']], 1):
                    print(f"  {i}. {h['title']}")
                    print(f"     Source: {h['description']}")
                    print(f"     Date: {h['date_info']}")
                    print(f"     URL: {h['url']}")
                    print()
        else:
            print("No new hackathons to post (all were duplicates)")
    else:
        print("No live hackathons found from any source")
        print("This could be due to:")
        print("  - Website structure changes")
        print("  - Anti-bot protection")
        print("  - Network issues")
        print("  - Sites requiring JavaScript")
    
    # Show database stats
    stats = db.get_stats()
    print(f"\nDATABASE STATS:")
    print(f"  Total hackathons: {stats['total_hackathons']}")
    print(f"  Posted to channel: {stats['posted_hackathons']}")
    print(f"  Pending: {stats['pending_hackathons']}")
    
    print("\nLive scraping completed!")

if __name__ == "__main__":
    asyncio.run(main())
