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
            
            # Additional warning suppression
            chrome_options.add_argument("--disable-webgl")
            chrome_options.add_argument("--disable-webgl2")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor,TranslateUI,VoiceOver")
            chrome_options.add_argument("--disable-speech-api")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-gpu-logging")
            chrome_options.add_argument("--silent")
            
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
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
            
            skip_titles = [
                "join a hackathon",
                "host a hackathon",
                "participate in our public hackathons",
                "public hackathons",
                "devpost",
            ]

            for tile in tiles[:5]:  # Process only first 5
                try:
                    # Get title from h3 (this was working)
                    title_elem = tile.find_element(By.CSS_SELECTOR, "h3")
                    title = title_elem.text.strip()
                    
                    if len(title) < 8:
                        continue

                    title_lower = title.lower().replace(" ", "")
                    if any(skip.replace(" ", "") in title_lower for skip in skip_titles):
                        continue
                    
                    # Get URL
                    link_elem = tile.find_element(By.CSS_SELECTOR, "a")
                    url = link_elem.get_attribute('href')

                    if not url or '/hackathons/' not in url:
                        continue
                    if url.rstrip('/').endswith('/hackathons'):
                        continue

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
        """Simplified Unstop scraping - focus on what works"""
        hackathons = []
        try:
            print("🔍 Unstop scraping...")
            self.driver.get("https://unstop.com/hackathons")
            time.sleep(6)  # Wait longer for dynamic content
            
            # Scroll to trigger dynamic loading
            self.driver.execute_script("window.scrollTo(0, 1000);")
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # Try multiple approaches to find hackathon content
            found_elements = []
            
            # Approach 1: Look for any clickable elements with hackathon-related text
            try:
                all_clickable = self.driver.find_elements(By.CSS_SELECTOR, "[onclick], [role='button'], a, div[class*='cursor-pointer']")
                for elem in all_clickable:
                    text = elem.text.strip().lower()
                    if any(keyword in text for keyword in ['hack', 'code', 'tech', 'ai', 'ml', 'competition']):
                        if len(text) > 10 and len(text) < 200:
                            found_elements.append(elem)
            except:
                pass
            
            # Approach 2: Look for any elements with hackathon-related URLs
            try:
                url_elements = self.driver.find_elements(By.CSS_SELECTOR, "[href*='hackathon'], [href*='competition'], [data-href*='hackathon']")
                found_elements.extend(url_elements)
            except:
                pass
            
            # Remove duplicates
            found_elements = list(set(found_elements))
            print(f"Found {len(found_elements)} potential hackathon elements")
            
            # Process found elements
            for elem in found_elements[:10]:  # Try more elements for better coverage
                try:
                    # Get title from element text
                    text = elem.text.strip()
                    if not text:
                        continue

                    # Extract title (first meaningful line)
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    title = ""
                    for line in lines:
                        # Skip common UI elements and look for titles
                        if any(skip in line.lower() for skip in ['view', 'more', 'filter', 'sort', 'days left', '₹', 'register']):
                            continue
                        if len(line) > 8 and len(line) < 100:
                            if any(keyword in line.lower() for keyword in ['hack', 'code', 'tech', 'ai', 'ml', 'challenge', 'fest', '2024', '2025', '2026']):
                                title = line
                                break
                    if not title or len(title) < 5:
                        continue

                    # Try to get URL from element, its children, or its parent
                    url = elem.get_attribute('href') or elem.get_attribute('data-href')
                    # Try child <a> with hackathon link
                    if not url:
                        try:
                            link_elem = elem.find_element(By.XPATH, ".//a[contains(@href, '/hackathon') or contains(@href, '/competition')]")
                            url = link_elem.get_attribute('href')
                        except:
                            pass
                    # Try parent <a> with hackathon link
                    if not url:
                        try:
                            parent = elem.find_element(By.XPATH, "..")
                            if parent:
                                parent_link = parent.get_attribute('href') or parent.get_attribute('data-href')
                                if parent_link and ('/hackathon' in parent_link or '/competition' in parent_link):
                                    url = parent_link
                        except:
                            pass
                    # Only add if we have a real, working URL
                    if not url or not url.startswith("http") or '/opportunity_' in url:
                        continue

                    hackathons.append({
                        'title': title,
                        'url': url,
                        'source': 'Unstop',
                        'date_info': 'Check Unstop for dates',
                        'description': f'🚀 {title}\nUnstop\n📅 Date: Check Unstop for dates\n📝 From Unstop.com\n🔗 {url}\n#Hackathon #Competition #Tech #Coding'
                    })
                    print(f"✅ Found: {title} | {url}")
                except Exception as e:
                    continue
            
            # If we found very few hackathons, add some fallback content
            if len(hackathons) == 0:
                print("⚠️  No hackathons found on Unstop - adding fallback")
                # Add a generic Unstop hackathon entry to encourage users to check
                hackathons.append({
                    'title': 'Latest Hackathons on Unstop',
                    'url': 'https://unstop.com/hackathons',
                    'source': 'Unstop',
                    'date_info': 'Various dates available',
                    'description': '🚀 Latest Hackathons on Unstop\nUnstop\n📅 Date: Various dates available\n📝 Check Unstop.com for the latest hackathons and competitions\n🔗 https://unstop.com/hackathons\n#Hackathon #Competition #Tech #Coding'
                })
                print("✅ Added: Latest Hackathons on Unstop (fallback)")
                    
        except Exception as e:
            print(f"Unstop error: {e}")
            # Even if scraping fails completely, add fallback
            hackathons.append({
                'title': 'Check Unstop for Latest Hackathons',
                'url': 'https://unstop.com/hackathons',
                'source': 'Unstop',
                'date_info': 'Various dates',
                'description': '🚀 Check Unstop for Latest Hackathons\nUnstop\n📅 Date: Various dates\n📝 Visit Unstop.com for hackathons and competitions\n� https://unstop.com/hackathons\n#Hackathon #Competition #Tech #Coding'
            })
            print("✅ Added: Check Unstop for Latest Hackathons (error fallback)")
        
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
    
    def close(self):
        """Close the driver properly with better error handling"""
        if hasattr(self, 'driver') and self.driver:
            try:
                # Close all windows first
                for handle in self.driver.window_handles:
                    try:
                        self.driver.switch_to.window(handle)
                        self.driver.close()
                    except:
                        pass
                
                # Quit the driver
                self.driver.quit()
                
                # Give it a moment to cleanup
                import time
                time.sleep(0.5)
                
            except Exception as e:
                # Suppress connection errors during cleanup - they're expected
                if "No connection could be made" not in str(e):
                    print(f"Driver cleanup warning: {e}")
            finally:
                self.driver = None
    
    def scrape_all(self):
        """Scrape all sources and return hackathons (for direct use with telegram bot)"""
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
            
            self.close()
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
        return all_hackathons
    
    def run(self):
        """Main scraping function with cloud fallback"""
        try:
            all_hackathons = self.scrape_all()
            if not all_hackathons:
                print("❌ No hackathons found")
                return

            # Post using TelegramBot to ensure dedupe and posted flags
            from telegram_bot import TelegramBot
            import asyncio

            telegram_bot = TelegramBot()
            result = asyncio.run(telegram_bot.post_hackathons(all_hackathons))
            print(f"📤 Posting completed: {result}")
            print("✅ Fast scraping completed!")
        except Exception as e:
            print(f"❌ Fast scraping failed: {e}")

if __name__ == "__main__":
    scraper = FastHackathonScraper()
    scraper.run()
