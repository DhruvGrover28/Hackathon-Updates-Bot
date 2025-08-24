#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

print("🔍 Testing website scraping...")

# Test MLH
print("\n=== MLH Events ===")
try:
    r = requests.get('https://mlh.io/events')
    soup = BeautifulSoup(r.text, 'html.parser')
    print(f"Status: {r.status_code}")
    
    # Look for event cards
    events = soup.find_all(['div', 'article'], class_=lambda x: x and 'event' in x.lower())
    print(f"Found {len(events)} event divs")
    
    # Look for any links with event in href
    event_links = soup.find_all('a', href=lambda x: x and 'event' in x)
    print(f"Found {len(event_links)} event links")
    
    for link in event_links[:3]:
        text = link.get_text(strip=True)
        if len(text) > 5:
            print(f"- {text[:50]} -> {link.get('href')}")
            
except Exception as e:
    print(f"MLH Error: {e}")

# Test DevPost
print("\n=== DevPost Hackathons ===")
try:
    r = requests.get('https://devpost.com/hackathons')
    soup = BeautifulSoup(r.text, 'html.parser')
    print(f"Status: {r.status_code}")
    
    # Look for hackathon tiles
    tiles = soup.find_all('div', class_=lambda x: x and 'tile' in x.lower())
    print(f"Found {len(tiles)} tiles")
    
    # Look for featured hackathons section
    featured = soup.find_all(['div', 'section'], class_=lambda x: x and 'featured' in x.lower())
    print(f"Found {len(featured)} featured sections")
    
    # Look for h2/h3 headers that might be hackathon names
    headers = soup.find_all(['h2', 'h3', 'h4'])
    hackathon_headers = [h for h in headers if h.get_text(strip=True) and len(h.get_text(strip=True)) > 10]
    print(f"Found {len(hackathon_headers)} potential hackathon headers")
    
    for header in hackathon_headers[:5]:
        text = header.get_text(strip=True)
        print(f"- {text}")
        
except Exception as e:
    print(f"DevPost Error: {e}")

# Test Unstop  
print("\n=== Unstop Hackathons ===")
try:
    r = requests.get('https://unstop.com/hackathons')
    soup = BeautifulSoup(r.text, 'html.parser')
    print(f"Status: {r.status_code}")
    
    # Look for competition cards
    cards = soup.find_all('div', class_=lambda x: x and 'card' in x.lower())
    print(f"Found {len(cards)} cards")
    
    # Look for links with /hackathons/ in href
    hack_links = soup.find_all('a', href=lambda x: x and '/hackathons/' in x)
    print(f"Found {len(hack_links)} hackathon links")
    
    for link in hack_links[:3]:
        text = link.get_text(strip=True)
        if len(text) > 5:
            print(f"- {text[:50]} -> {link.get('href')}")
            
except Exception as e:
    print(f"Unstop Error: {e}")

print("\n✅ Site testing completed!")
