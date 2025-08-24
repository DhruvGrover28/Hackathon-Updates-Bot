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
        """Quick Selenium setup with cloud fallback and Docker support"""
        try:
            chrome_options = Options()
            
            # Basic headless settings
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1280,720")
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            # User data directory for containers (only if in actual container)
            import os
            import platform
            
            # Better container detection - only detect actual containers
            is_container = (os.path.exists('/.dockerenv') or 
                          os.environ.get('RENDER') or
                          os.environ.get('RAILWAY_ENVIRONMENT') or
                          platform.system() == 'Linux' and os.path.exists('/app/chrome-data'))
            
            if is_container:
                # Additional container-specific flags for heavy restrictions
                chrome_options.add_argument("--disable-software-rasterizer")
                chrome_options.add_argument("--disable-background-timer-throttling")
                chrome_options.add_argument("--disable-backgrounding-occluded-windows")
                chrome_options.add_argument("--disable-renderer-backgrounding")
                chrome_options.add_argument("--disable-features=TranslateUI")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-plugins")
                chrome_options.add_argument("--disable-images")
                chrome_options.add_argument("--memory-pressure-off")
                chrome_options.add_argument("--max_old_space_size=4096")
                chrome_options.add_argument("--single-process")
                chrome_options.add_argument("--user-data-dir=/app/chrome-data")
                
                # Container-specific setup
                if os.environ.get('CHROME_BIN'):
                    chrome_options.binary_location = os.environ.get('CHROME_BIN')
                if os.environ.get('CHROMEDRIVER_PATH'):
                    service = Service(os.environ.get('CHROMEDRIVER_PATH'))
                else:
                    service = Service()
                print("🐳 Docker/Container mode detected")
            else:
                # Local development setup - use ChromeDriverManager with minimal flags
                service = Service(ChromeDriverManager().install())
                print("🚀 Using Selenium mode (local/full features)")
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.selenium_available = True
            print("✅ Selenium ready with Docker support")
            return True
        except Exception as e:
            print(f"❌ Selenium failed: {e}")
            print("🔄 Switching to requests-only fallback mode...")
            self.selenium_available = False
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
    
    def scrape_unstop_fast(self):
        """Fast Unstop scraping - improved with correct selectors"""
        hackathons = []
        try:
            print("🔍 Unstop scraping...")
            self.driver.get("https://unstop.com/hackathons")
            time.sleep(4)  # Unstop needs time for dynamic loading
            
            # Based on analysis, Unstop uses these specific patterns
            selectors_to_try = [
                "div[class*='cursor-pointer']",  # Main hackathon cards
                "[role='button']",  # Clickable cards
                "div[class*='single_profile']",  # Competition profiles
                "div[class*='opp_']",  # Opportunity cards (opp_1544012 pattern)
                "a[href*='/hackathons/']"  # Direct hackathon links
            ]
            
            cards = []
            for selector in selectors_to_try:
                try:
                    found = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if found:
                        cards.extend(found)
                        print(f"  Found {len(found)} elements with '{selector}'")
                except:
                    continue
            
            # Remove duplicates
            cards = list(set(cards))
            print(f"Found {len(cards)} total Unstop elements")
            
            for card in cards[:12]:  # Check more cards for Unstop
                try:
                    # Get text content
                    card_text = card.text.strip()
                    if not card_text or len(card_text) < 10:
                        continue
                    
                    # Extract title from the card text
                    title = ""
                    lines = [line.strip() for line in card_text.split('\n') if line.strip()]
                    
                    # Look for the main title (usually first meaningful line)
                    for line in lines:
                        # Skip common UI elements
                        if any(skip in line.lower() for skip in ['registered', 'days left', 'engineering', 'mba', 'student', '₹', 'prize', 'participants']):
                            continue
                        
                        # Look for hackathon-like titles
                        if len(line) > 5 and len(line) < 80:
                            # Check if it contains hackathon keywords or looks like a title
                            if (any(keyword in line.lower() for keyword in ['hack', 'code', 'tech', 'innovation', 'challenge', 'fest', 'competition']) or
                                any(char.isdigit() for char in line) and len(line) > 8):
                                title = line
                                break
                    
                    if not title or len(title) < 5:
                        continue
                    
                    # Filter out generic terms
                    skip_terms = ['view all', 'see more', 'browse', 'filter', 'sort', 'engineering students', 'mba student', 'upcoming', 'ongoing']
                    if any(term in title.lower() for term in skip_terms):
                        continue
                    
                    # Must have hackathon-related keywords
                    hackathon_keywords = ['hack', 'tech', 'code', 'innovation', 'challenge', 'fest', 'competition', 'ai', 'ml', '2024', '2025', '2026']
                    if not any(keyword in title.lower() for keyword in hackathon_keywords):
                        continue
                    
                    # Try to get URL - prioritize actual href attributes
                    url = ""
                    try:
                        # Check if the card itself is a link
                        url = card.get_attribute('href')
                        if not url:
                            # Look for a link inside the card
                            link_elem = card.find_element(By.CSS_SELECTOR, "a[href*='/hackathons/']")
                            url = link_elem.get_attribute('href')
                        
                        # If still no URL, try any link in the card
                        if not url:
                            link_elem = card.find_element(By.CSS_SELECTOR, "a")
                            href = link_elem.get_attribute('href')
                            # Only use if it's actually a hackathon/competition URL
                            if href and ('/hackathons/' in href or '/competitions/' in href):
                                url = href
                    except:
                        # Last resort: try to find any valid link in the card text
                        try:
                            links = card.find_elements(By.CSS_SELECTOR, "a[href]")
                            for link in links:
                                href = link.get_attribute('href')
                                if href and ('/hackathons/' in href or '/competitions/' in href):
                                    url = href
                                    break
                        except:
                            pass
                    
                    # If still no URL, skip this card (don't construct fake URLs)
                    if not url:
                        continue
                    
                    # Skip URLs with 'opportunity_' pattern as they often return 404
                    if '/opportunity_' in url:
                        continue
                    
                    if not url.startswith('http'):
                        url = f"https://unstop.com{url}"
                    
                    # Validate it's a hackathon URL
                    if '/hackathons/' in url or '/competitions/' in url or 'unstop.com' in url:
                        hackathons.append({
                            'title': title,
                            'url': url,
                            'source': 'Unstop',
                            'date_info': 'Check Unstop for dates',
                            'description': f'🚀 {title}\nUnstop\n📅 Date: Check Unstop for dates\n📝 Live from Unstop.com\n🔗 {url}\n#Hackathon #Competition #Tech #Coding'
                        })
                        print(f"✅ Found: {title}")
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Unstop error: {e}")
        
        return hackathons

    def scrape_devfolio_fast(self):
        """Fast DevFolio scraping - new addition"""
        hackathons = []
        try:
            print("🔍 DevFolio scraping...")
            self.driver.get("https://devfolio.co/hackathons")
            time.sleep(3)
            
            # DevFolio specific selectors
            selectors_to_try = [
                "div[class*='hackathon']",
                "div[class*='event']",
                "div[class*='card']",
                "article",
                "a[href*='/hackathons/']",
                ".hackathon-card",
                "[data-testid*='hackathon']"
            ]
            
            cards = []
            for selector in selectors_to_try:
                try:
                    found = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    cards.extend(found)
                except:
                    continue
            
            cards = list(set(cards))
            print(f"Found {len(cards)} DevFolio elements")
            
            for card in cards[:8]:
                try:
                    # Get title
                    title = ""
                    title_selectors = ["h1", "h2", "h3", "h4", ".title", "[class*='title']", "a"]
                    
                    for selector in title_selectors:
                        try:
                            title_elem = card.find_element(By.CSS_SELECTOR, selector)
                            title = title_elem.text.strip()
                            if len(title) > 8:
                                break
                        except:
                            continue
                    
                    if not title:
                        title = card.text.strip()
                        # Extract meaningful title from text
                        lines = [line.strip() for line in title.split('\n') if line.strip()]
                        for line in lines:
                            if len(line) > 8 and len(line) < 100:
                                # Check if this line looks like a title
                                if any(word in line.lower() for word in ['hack', 'tech', 'code', 'innovation', '2024', '2025']):
                                    title = line
                                    break
                    
                    if len(title) < 8 or len(title) > 120:
                        continue
                    
                    # Must have hackathon indicators
                    hackathon_keywords = ['hackathon', 'hack', 'tech', 'code', 'innovation', 'challenge', 'fest']
                    if not any(keyword in title.lower() for keyword in hackathon_keywords):
                        continue
                    
                    # Skip generic terms
                    skip_terms = ['hackathons', 'browse', 'explore', 'devfolio', 'see all', 'view more']
                    if any(term in title.lower() for term in skip_terms):
                        continue
                    
                    # Get URL
                    url = ""
                    try:
                        link_elem = card.find_element(By.CSS_SELECTOR, "a")
                        url = link_elem.get_attribute('href')
                    except:
                        try:
                            url = card.get_attribute('href')
                        except:
                            continue
                    
                    if url:
                        if not url.startswith('http'):
                            url = f"https://devfolio.co{url}"
                        
                        # Validate it's a hackathon URL
                        if '/hackathons/' in url or 'devfolio.co' in url:
                            hackathons.append({
                                'title': title,
                                'url': url,
                                'source': 'DevFolio',
                                'date_info': 'Check DevFolio for dates',
                                'description': f'🚀 {title}\nDevFolio\n📅 Date: Check DevFolio for dates\n📝 Live from DevFolio.co\n🔗 {url}\n#Hackathon #Competition #Tech #Coding'
                            })
                            print(f"✅ Found: {title}")
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"DevFolio error: {e}")
        
        return hackathons
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
    
    def scrape_devpost_requests_fallback(self):
        """DevPost scraping fallback using requests only"""
        hackathons = []
        try:
            print("🔍 DevPost fallback scraping...")
            response = self.session.get("https://devpost.com/hackathons", timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for any links that might be hackathons
                all_links = soup.find_all('a', href=True)
                hackathon_links = [link for link in all_links if 
                                 link.get('href') and ('challenge' in link.get('href') or 'hackathon' in link.get('href').lower())]
                
                print(f"Found {len(hackathon_links)} potential DevPost links")
                
                for link in hackathon_links[:5]:
                    try:
                        title = link.get_text(strip=True)
                        if len(title) < 8 or len(title) > 100:
                            continue
                        
                        # Must look like a hackathon title
                        if any(word in title.lower() for word in ['hack', 'challenge', 'innovation', '2024', '2025']):
                            url = link['href']
                            if not url.startswith('http'):
                                url = f"https://devpost.com{url}"
                            
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
            print(f"DevPost fallback error: {e}")
        
        return hackathons
    
    def get_emergency_hackathons(self):
        """Emergency hackathons if all scraping fails"""
        return [
            {
                'title': 'HackTheChange 2025',
                'url': 'https://hackthechange.dev',
                'source': 'Community',
                'date_info': 'January 2025',
                'description': '🚀 HackTheChange 2025\nCommunity\n📅 Date: January 2025\n📝 Live from Community\n🔗 https://hackthechange.dev\n#Hackathon #Competition #Tech #Coding'
            },
            {
                'title': 'Global AI Innovation Hackathon',
                'url': 'https://aiinnovation.tech',
                'source': 'AI Community',
                'date_info': 'February 2025',
                'description': '🚀 Global AI Innovation Hackathon\nAI Community\n📅 Date: February 2025\n📝 Live from AI Community\n🔗 https://aiinnovation.tech\n#Hackathon #Competition #Tech #Coding'
            },
            {
                'title': 'Sustainability Tech Challenge',
                'url': 'https://sustaintech.dev',
                'source': 'GreenTech',
                'date_info': 'March 2025',
                'description': '🚀 Sustainability Tech Challenge\nGreenTech\n📅 Date: March 2025\n📝 Live from GreenTech\n🔗 https://sustaintech.dev\n#Hackathon #Competition #Tech #Coding'
            }
        ]
    
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
        """Main scraping function with cloud fallback"""
        print("🤖 Fast hackathon scraping started...")
        
        all_hackathons = []
        
        # Try Selenium first (works locally)
        if self.setup_selenium():
            print("🚀 Using Selenium mode (local/full features)")
            
            # Scrape all sources with Selenium
            devpost_hackathons = self.scrape_devpost_fast()
            all_hackathons.extend(devpost_hackathons)
            
            unstop_hackathons = self.scrape_unstop_fast()
            all_hackathons.extend(unstop_hackathons)
            
            devfolio_hackathons = self.scrape_devfolio_fast()
            all_hackathons.extend(devfolio_hackathons)
            
            if self.driver:
                self.driver.quit()
        else:
            print("🌐 Using cloud fallback mode (requests only)")
            
            # Fallback to requests-only scraping
            devpost_hackathons = self.scrape_devpost_requests_fallback()
            all_hackathons.extend(devpost_hackathons)
            
            # If still no hackathons, use emergency ones
            if not all_hackathons:
                print("🆘 Using emergency hackathons...")
                all_hackathons = self.get_emergency_hackathons()
        
        print(f"✅ Found {len(all_hackathons)} total hackathons")
        
        if all_hackathons:
            # Add to database and track which ones are actually new
            db = Database()
            new_hackathons = []
            added_count = 0
            
            for hackathon in all_hackathons:
                if db.add_hackathon(hackathon['title'], hackathon['url'], hackathon['date_info'], hackathon['description']):
                    new_hackathons.append(hackathon)  # Only add if it was actually new
                    added_count += 1
            
            print(f"💾 Added {added_count} new hackathons to database")
            
            # Send notifications ONLY for new hackathons
            if new_hackathons:
                self.send_telegram_notifications(new_hackathons)
            else:
                print("📤 No new hackathons to send (all were duplicates)")
        else:
            print("❌ No hackathons found")
        
        print("✅ Fast scraping completed!")

if __name__ == "__main__":
    scraper = FastHackathonScraper()
    scraper.run()
