#!/usr/bin/env python3
# Quick test to see what DevPost cards contain
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

print("🔍 Quick DevPost test...")

try:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get("https://devpost.com/hackathons")
    time.sleep(3)
    
    # Try to find hackathon tiles
    tiles = driver.find_elements(By.CSS_SELECTOR, ".hackathon-tile")
    print(f"Found {len(tiles)} hackathon tiles")
    
    for i, tile in enumerate(tiles[:3]):
        print(f"\n=== Tile {i+1} ===")
        try:
            text = tile.text.strip()
            print(f"Text: {text[:100]}...")
            
            # Try to find title
            title_elem = tile.find_element(By.CSS_SELECTOR, "h3, h2, h1, .title")
            if title_elem:
                print(f"Title: {title_elem.text.strip()}")
                
            # Try to find link
            link_elem = tile.find_element(By.CSS_SELECTOR, "a")
            if link_elem:
                print(f"Link: {link_elem.get_attribute('href')}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    # Also try alternative selectors
    print(f"\n=== Alternative approach ===")
    hackathon_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/challenges/')]")
    print(f"Found {len(hackathon_links)} challenge links")
    
    for i, link in enumerate(hackathon_links[:3]):
        try:
            text = link.text.strip()
            href = link.get_attribute('href')
            if text and len(text) > 5:
                print(f"{i+1}. {text} -> {href}")
        except:
            continue
    
    driver.quit()
    print("✅ DevPost test completed!")
    
except Exception as e:
    print(f"Error: {e}")
