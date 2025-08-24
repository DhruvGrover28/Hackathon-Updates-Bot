#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robust scraper - Tries Selenium first, falls back to requests gracefully
Fixed version with proper error handling and structure
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
    from selenium.webdriver.common.by import By
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    By = None

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
        """Try selenium-based scraping directly without subprocess"""
        try:
            print("🚀 Running Selenium-based scraping...")
            
            if not self.selenium_available:
                print("❌ Selenium not available, skipping...")
                return False
            
            hackathons = []
            
            # Scrape Unstop with Selenium
            try:
                self.driver.get("https://unstop.com/hackathons")
                time.sleep(3)
                
                # Look for hackathon cards
                cards = self.driver.find_elements(By.CSS_SELECTOR, "[class*='card'], [class*='competition'], [class*='opportunity']")
                
                for card in cards[:10]:  # Limit to avoid too many
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, "h3, h2, .title, [class*='title']")
                        title = title_elem.text.strip()
                        
                        if len(title) > 10 and not any(skip in title.lower() for skip in ['join', 'participate', 'explore']):
                            link_elem = card.find_element(By.CSS_SELECTOR, "a")
                            url = link_elem.get_attribute('href')
                            
                            if url and '/hackathons/' in url:
                                hackathons.append({
                                    'title': title,
                                    'url': url,
                                    'source': 'Unstop',
                                    'date_info': 'Check website for dates',
                                    'description': f'Hackathon from Unstop: {title}'
                                })
                    except:
                        continue
                        
            except Exception as e:
                print(f"Error scraping Unstop with Selenium: {e}")
            
            # Add hackathons to database
            if hackathons:
                db = Database()
                added_count = 0
                for hackathon in hackathons:
                    if db.add_hackathon(hackathon['title'], hackathon['url'], hackathon['date_info'], hackathon['description']):
                        added_count += 1
                
                print(f"✅ Added {added_count} new hackathons via Selenium")
                return True
            else:
                print("❌ No hackathons found with Selenium")
                return False
                
        except Exception as e:
            print(f"❌ Error with Selenium scraping: {e}")
            return False
    
    def scrape_with_requests_fallback(self):
        """Fallback requests-only scraping - Get real hackathon data"""
        try:
            print("🔄 Using requests-only fallback mode...")
            
            hackathons = []
            
            # Method 1: Scrape Unstop.com directly with better targeting
            try:
                print("🔍 Scraping Unstop.com...")
                response = self.session.get("https://unstop.com/hackathons", timeout=20)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # More specific selectors for Unstop
                    # Try different approaches to find hackathon cards
                    
                    # Approach 1: Look for competition cards
                    cards = soup.find_all(['div'], class_=lambda x: x and any(
                        keyword in x.lower() for keyword in ['competition-card', 'event-card', 'opportunity-card']
                    ))
                    
                    # Approach 2: Look for article tags
                    if not cards:
                        cards = soup.find_all(['article', 'div'], class_=lambda x: x and any(
                            keyword in x.lower() for keyword in ['card', 'item', 'list-item']
                        ))
                    
                    # Approach 3: Look for divs containing hackathon links
                    if not cards:
                        all_links = soup.find_all('a', href=lambda x: x and '/hackathons/' in x)
                        cards = [link.find_parent(['div', 'article']) for link in all_links if link.find_parent(['div', 'article'])]
                        cards = [card for card in cards if card]  # Remove None values
                    
                    print(f"Found {len(cards)} potential Unstop hackathon elements")
                    
                    for card in cards[:8]:  # Limit to first 8
                        try:
                            # Extract title - be more specific
                            title_elem = card.find(['h1', 'h2', 'h3', 'h4'], 
                                                  class_=lambda x: x and any(
                                                      keyword in x.lower() for keyword in ['title', 'name', 'heading']
                                                  ))
                            
                            if not title_elem:
                                # Look for any heading in the card
                                title_elem = card.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                            
                            if not title_elem:
                                # Look for the main link text
                                link_elem = card.find('a', href=lambda x: x and '/hackathons/' in x)
                                if link_elem:
                                    title_elem = link_elem
                            
                            if not title_elem:
                                continue
                                
                            title = title_elem.get_text(strip=True)
                            
                            # Filter out navigation and generic text
                            if not title or len(title) < 10:
                                continue
                            
                            # Skip generic/navigation items
                            skip_terms = ['view all', 'see more', 'browse', 'filter', 'sort', 'search', 'menu', 'nav']
                            if any(term in title.lower() for term in skip_terms):
                                continue
                            
                            # Must contain hackathon-related terms
                            if not any(keyword in title.lower() for keyword in ['hackathon', 'hack', 'coding', 'development', 'tech', 'innovation', 'challenge']):
                                continue
                            
                            # Extract link
                            link_elem = card.find('a', href=True)
                            link = ""
                            if link_elem and '/hackathons/' in link_elem['href']:
                                href = link_elem['href']
                                if href.startswith('/'):
                                    link = f"https://unstop.com{href}"
                                elif href.startswith('http'):
                                    link = href
                            
                            # Look for date/deadline info
                            date_text = "Check Unstop for dates"
                            
                            # Look for deadline in various formats
                            date_keywords = ['deadline', 'last date', 'submit by', 'ends on', 'closes', 'due']
                            for keyword in date_keywords:
                                date_elem = card.find(string=lambda text: text and keyword in text.lower())
                                if date_elem:
                                    # Try to extract the date part
                                    import re
                                    date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{1,2}\s+\w+\s+\d{2,4})', date_elem.parent.get_text())
                                    if date_match:
                                        date_text = date_match.group(1)
                                        break
                            
                            # Look for organization/location
                            org_elem = card.find(['p', 'span', 'div'], class_=lambda x: x and any(
                                keyword in x.lower() for keyword in ['org', 'location', 'institute', 'company', 'by']
                            ))
                            organization = ""
                            if org_elem:
                                org_text = org_elem.get_text(strip=True)
                                if len(org_text) < 100:  # Avoid long descriptions
                                    organization = org_text
                            
                            # Only add if we have a proper link
                            if link:
                                hackathon = {
                                    'title': title,
                                    'link': link,
                                    'deadline': date_text,
                                    'source': 'Unstop',
                                    'organization': organization
                                }
                                hackathons.append(hackathon)
                                print(f"📝 Found: {title}")
                                
                        except Exception as e:
                            print(f"Error processing Unstop card: {e}")
                            continue
                            
            except Exception as e:
                print(f"❌ Unstop scraping failed: {e}")
            
            # Method 2: Scrape DevPost
            try:
                print("🔍 Scraping DevPost.com...")
                response = self.session.get("https://devpost.com/hackathons", timeout=20)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # DevPost specific selectors - try multiple approaches
                    cards = soup.find_all(['div'], class_=lambda x: x and 'hackathon-tile' in x.lower())
                    
                    if not cards:
                        cards = soup.find_all(['div', 'article'], class_=lambda x: x and any(
                            keyword in x.lower() for keyword in ['hackathon', 'challenge', 'event']
                        ))
                    
                    if not cards:
                        # Look for any cards with hackathon-related content
                        all_divs = soup.find_all('div')
                        cards = [div for div in all_divs if div.find(string=lambda t: t and any(
                            word in t.lower() for word in ['hackathon', 'hack ', 'coding challenge']
                        ))]
                    
                    print(f"Found {len(cards)} potential DevPost events")
                    
                    for card in cards[:8]:  # Increase limit to 8
                        try:
                            # More aggressive title searching
                            title_elem = card.find(['h1', 'h2', 'h3', 'h4', 'a']) 
                            if not title_elem:
                                # Look for any text that looks like a title
                                title_elem = card.find(string=lambda t: t and len(t.strip()) > 15 and any(
                                    word in t.lower() for word in ['hackathon', 'challenge', 'hack']
                                ))
                                if title_elem:
                                    title = title_elem.strip()
                                else:
                                    continue
                            else:
                                title = title_elem.get_text(strip=True)
                            
                            if not title or len(title) < 8:
                                continue
                            
                            # Filter out navigation and generic items for DevPost
                            skip_terms = [
                                'join a hackathon', 'participate in', 'devpost', 'access your', 
                                'for teams', 'hackathons', 'challenges', 'events', 'browse',
                                'see all', 'view more', 'explore', 'find hackathons', 
                                'public hackathons', 'company\'s private', 'register now'
                            ]
                            if any(term in title.lower() for term in skip_terms):
                                continue
                            
                            # Must look like a real hackathon name with specific words/numbers
                            # Real hackathons usually have: numbers, specific names, tech terms
                            valid_indicators = [
                                any(char.isdigit() for char in title),  # Has numbers (version, year)
                                any(word in title.lower() for word in ['2024', '2025', 'ai', 'ml', 'web3', 'crypto', 'tech', 'data', 'climate', 'health', 'fintech']),
                                len(title.split()) >= 2 and len(title) > 20  # Multi-word, descriptive title
                            ]
                            
                            if not any(valid_indicators):
                                continue
                            
                            # Extract link
                            link_elem = card.find('a', href=True)
                            link = ""
                            if link_elem:
                                href = link_elem['href']
                                if href.startswith('/'):
                                    link = f"https://devpost.com{href}"
                                elif href.startswith('http'):
                                    link = href
                            
                            # Look for date info more aggressively
                            date_text = "Check DevPost for dates"
                            
                            # Try to find date in various formats
                            date_patterns = [
                                r'deadline[:\s]+([^<\n]+)',
                                r'due[:\s]+([^<\n]+)',
                                r'ends[:\s]+([^<\n]+)',
                                r'submit by[:\s]+([^<\n]+)'
                            ]
                            
                            import re
                            card_text = card.get_text()
                            for pattern in date_patterns:
                                match = re.search(pattern, card_text, re.IGNORECASE)
                                if match:
                                    date_text = match.group(1).strip()
                                    break
                            
                            # Look for sponsor/organization
                            org_elem = card.find(['span', 'div'], class_=lambda x: x and any(
                                keyword in x.lower() for keyword in ['sponsor', 'host', 'by']
                            ))
                            organization = "DevPost Community"
                            if org_elem:
                                organization = org_elem.get_text(strip=True)
                            
                            # Only add if it looks like a real hackathon
                            if any(keyword in title.lower() for keyword in ['hackathon', 'hack ', 'challenge', 'coding']):
                                hackathon = {
                                    'title': title,
                                    'link': link or "https://devpost.com/hackathons",
                                    'deadline': date_text,
                                    'source': 'DevPost',
                                    'organization': organization
                                }
                                hackathons.append(hackathon)
                                print(f"📝 Found: {title}")
                            
                        except Exception as e:
                            print(f"Error processing DevPost card: {e}")
                            continue
                            
            except Exception as e:
                print(f"❌ DevPost scraping failed: {e}")
            
            # Method 3: Try MLH (Major League Hacking)
            try:
                print("🔍 Scraping MLH...")
                response = self.session.get("https://mlh.io/events", timeout=20)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for event cards
                    events = soup.find_all(['div', 'article'], class_=lambda x: x and any(
                        keyword in x.lower() for keyword in ['event', 'hackathon']
                    ))
                    
                    print(f"Found {len(events)} potential MLH events")
                    
                    for event in events[:5]:
                        try:
                            title_elem = event.find(['h1', 'h2', 'h3', 'h4', 'a'])
                            if not title_elem:
                                continue
                                
                            title = title_elem.get_text(strip=True)
                            
                            if not title or len(title) < 8:
                                continue
                            
                            # Extract link
                            link_elem = event.find('a', href=True)
                            link = ""
                            if link_elem:
                                href = link_elem['href']
                                if href.startswith('/'):
                                    link = f"https://mlh.io{href}"
                                elif href.startswith('http'):
                                    link = href
                            
                            # Look for date
                            date_text = "Check MLH for dates"
                            date_elem = event.find(string=lambda text: text and any(
                                keyword in text.lower() for keyword in ['2024', '2025', 'sep', 'oct', 'nov', 'dec', 'jan', 'feb']
                            ))
                            if date_elem:
                                date_text = date_elem.strip()
                            
                            if 'hack' in title.lower():
                                hackathon = {
                                    'title': title,
                                    'link': link or "https://mlh.io/events",
                                    'deadline': date_text,
                                    'source': 'MLH',
                                    'organization': 'Major League Hacking'
                                }
                                hackathons.append(hackathon)
                                print(f"📝 Found: {title}")
                                
                        except Exception as e:
                            print(f"Error processing MLH event: {e}")
                            continue
                            
            except Exception as e:
                print(f"❌ MLH scraping failed: {e}")
            
            # Return only real hackathons found
            if len(hackathons) > 0:
                print(f"✅ Found {len(hackathons)} real hackathons!")
            else:
                print("❌ No real hackathons found in this scraping session")
            
            return hackathons
            
        except Exception as e:
            print(f"❌ Fallback scraping failed: {e}")
            return []
    
    def send_telegram_notifications(self, hackathons):
        """Send notifications to Telegram"""
        try:
            load_dotenv()
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
            
            if not bot_token or not channel_id:
                print("❌ Telegram credentials not found")
                return
            
            print(f"📤 Sending {len(hackathons)} notifications to {channel_id}")
            
            for hackathon in hackathons:
                # Format message like your example (without emojis in title)
                organization_line = ""
                if hackathon.get('organization') and hackathon['organization']:
                    organization_line = f"{hackathon['organization']}\n"
                
                message = f"""🚀 {hackathon['title']}
{organization_line}
📅 Date: {hackathon['deadline']}

📝 Live from {hackathon['source']}.com (Requests fallback)

🔗 {hackathon['link']}

#Hackathon #Competition #Tech #Coding"""
                
                # Send via Telegram API directly
                telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                data = {
                    'chat_id': channel_id,
                    'text': message,
                    'parse_mode': 'Markdown',
                    'disable_web_page_preview': True
                }
                
                try:
                    response = requests.post(telegram_url, data=data, timeout=10)
                    if response.status_code == 200:
                        print(f"✅ Sent notification for: {hackathon['title']}")
                    else:
                        print(f"❌ Failed to send notification: {response.text}")
                except Exception as e:
                    print(f"❌ Error sending to Telegram: {e}")
                
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            print(f"❌ Error in Telegram notifications: {e}")
    
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
                    newly_added = []
                    
                    # Process each hackathon
                    for hackathon in hackathons:
                        if db.add_hackathon(
                            title=hackathon['title'],
                            url=hackathon['link'],
                            date_info=hackathon['deadline'],
                            description=f"Source: {hackathon['source']} | Org: {hackathon.get('organization', 'N/A')}"
                        ):
                            new_count += 1
                            newly_added.append(hackathon)
                    
                    print(f"💾 Added {new_count} new hackathons to database")
                    
                    # Send notifications for new hackathons only
                    if new_count > 0:
                        self.send_telegram_notifications(newly_added)
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
