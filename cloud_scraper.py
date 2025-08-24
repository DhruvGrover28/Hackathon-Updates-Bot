#!/usr/bin/env python3
"""
Cloud-compatible scraper - No Selenium, only requests for Render deployment
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

class CloudHackathonScraper:
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
    
    def scrape_unstop_simple(self):
        """Simple Unstop scraper using only requests"""
        hackathons = []
        
        try:
            print("Scraping Unstop.com (cloud-compatible mode)...")
            
            url = "https://unstop.com/hackathons"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for hackathon cards
                cards = soup.find_all(['div', 'article'], class_=lambda x: x and any(
                    keyword in x.lower() for keyword in ['card', 'event', 'hackathon', 'item', 'post']
                ))
                
                print(f"Found {len(cards)} potential hackathon elements")
                
                for card in cards[:10]:  # Limit to first 10
                    try:
                        # Extract title
                        title_elem = card.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'], 
                                              class_=lambda x: x and any(
                                                  keyword in x.lower() for keyword in ['title', 'name', 'heading']
                                              ))
                        
                        if not title_elem:
                            title_elem = card.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                        
                        if not title_elem:
                            continue
                            
                        title = title_elem.get_text(strip=True)
                        
                        if not title or len(title) < 10:
                            continue
                        
                        # Extract link
                        link_elem = card.find('a', href=True)
                        link = ""
                        if link_elem:
                            href = link_elem['href']
                            if href.startswith('/'):
                                link = f"https://unstop.com{href}"
                            elif href.startswith('http'):
                                link = href
                        
                        # Look for date info
                        date_text = ""
                        date_elem = card.find(text=lambda text: text and any(
                            keyword in text.lower() for keyword in ['deadline', 'submit', 'ends', 'closes', 'until', 'due']
                        ))
                        if date_elem:
                            date_text = date_elem.strip()
                        
                        # Basic hackathon detection
                        if any(keyword in title.lower() for keyword in ['hackathon', 'hack', 'coding', 'development', 'tech', 'innovation']):
                            hackathon = {
                                'title': title,
                                'link': link or "https://unstop.com/hackathons",
                                'deadline': date_text or "Check website",
                                'source': 'Unstop'
                            }
                            hackathons.append(hackathon)
                            print(f"Found: {title}")
                            
                    except Exception as e:
                        print(f"Error processing card: {e}")
                        continue
                        
            else:
                print(f"Failed to fetch Unstop: {response.status_code}")
                
        except Exception as e:
            print(f"Error scraping Unstop: {e}")
        
        return hackathons
    
    def scrape_devpost_simple(self):
        """Simple DevPost scraper using only requests"""
        hackathons = []
        
        try:
            print("Scraping DevPost.com (cloud-compatible mode)...")
            
            url = "https://devpost.com/hackathons"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # DevPost specific selectors
                cards = soup.find_all(['div', 'article'], class_=lambda x: x and 'hackathon' in x.lower())
                
                if not cards:
                    cards = soup.find_all(['div'], class_=lambda x: x and any(
                        keyword in x.lower() for keyword in ['card', 'item', 'event']
                    ))
                
                print(f"Found {len(cards)} potential DevPost events")
                
                for card in cards[:5]:  # Limit to first 5
                    try:
                        title_elem = card.find(['h1', 'h2', 'h3', 'h4', 'a'])
                        if not title_elem:
                            continue
                            
                        title = title_elem.get_text(strip=True)
                        
                        if not title or len(title) < 10:
                            continue
                        
                        link_elem = card.find('a', href=True)
                        link = ""
                        if link_elem:
                            href = link_elem['href']
                            if href.startswith('/'):
                                link = f"https://devpost.com{href}"
                            elif href.startswith('http'):
                                link = href
                        
                        hackathon = {
                            'title': title,
                            'link': link or "https://devpost.com/hackathons",
                            'deadline': "Check website",
                            'source': 'DevPost'
                        }
                        hackathons.append(hackathon)
                        print(f"Found: {title}")
                        
                    except Exception as e:
                        print(f"Error processing DevPost card: {e}")
                        continue
                        
            else:
                print(f"Failed to fetch DevPost: {response.status_code}")
                
        except Exception as e:
            print(f"Error scraping DevPost: {e}")
        
        return hackathons
    
    def run_cloud_scraping(self):
        """Run cloud-compatible scraping without Selenium"""
        all_hackathons = []
        
        try:
            # Scrape Unstop
            unstop_hackathons = self.scrape_unstop_simple()
            all_hackathons.extend(unstop_hackathons)
            
            time.sleep(2)  # Be nice to servers
            
            # Scrape DevPost
            devpost_hackathons = self.scrape_devpost_simple()
            all_hackathons.extend(devpost_hackathons)
            
            print(f"Total hackathons found: {len(all_hackathons)}")
            
            if all_hackathons:
                # Save to database
                db = Database()
                new_count = 0
                
                for hackathon in all_hackathons:
                    if db.add_hackathon(hackathon):
                        new_count += 1
                
                print(f"Added {new_count} new hackathons to database")
                
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
**New Hackathon Alert!**

**{hackathon['title']}**

**Source:** {hackathon['source']}
**Deadline:** {hackathon['deadline']}
**Link:** {hackathon['link']}

Join now and start building!
"""
                            success = bot.send_message(channel_id, message)
                            if success:
                                print(f"Sent notification for: {hackathon['title']}")
                            time.sleep(1)  # Rate limiting
                    else:
                        print("Telegram credentials not found - skipping notifications")
                else:
                    print("No new hackathons to notify about")
            else:
                print("No hackathons found in this run")
                
        except Exception as e:
            print(f"Error in cloud scraping: {e}")
            
def main():
    """Main function for cloud scraping"""
    print("Starting cloud-compatible hackathon scraping...")
    scraper = CloudHackathonScraper()
    scraper.run_cloud_scraping()
    print("Cloud scraping completed!")

if __name__ == "__main__":
    main()
