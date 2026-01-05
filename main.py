import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. SETUP TELEGRAM ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_alert(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Keys missing!")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

# --- 2. SETUP BROWSER ---
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") # The modern headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# --- 3. THE SCRAPER ---
def check_changi():
    driver = get_driver()
    print("🚀 Launching cloud browser...")
    
    try:
        driver.get("https://www.changiairport.com/en/flights/arrivals.html")
        time.sleep(8) # Wait for Changi's fancy animations to load
        
        # STRATEGY: Find all elements that look like flight times
        # Note: These class names are GUESSES. You must verify them (See Phase 4 below)
        # Often Changi uses classes like "flight-time" or "col-time"
        
        # Let's try to grab the whole row first
        flight_rows = driver.find_elements(By.CLASS_NAME, "flight-card") 
        
        flight_count = len(flight_rows)
        print(f"🔎 Found {flight_count} flights listed.")

        if flight_count > 5:
            msg = f"✈️ **Airport Demand Spike!**\n\n"
            msg += f"I found **{flight_count} incoming flights** on the board.\n"
            msg += "This might be a good time to head to the queue!\n\n"
            msg += "_(Data sourced from Changi Public Arrivals)_"
            
            send_alert(msg)
            print("✅ Alert sent.")
        else:
            print("📉 Traffic looks normal. No alert sent.")

    except Exception as e:
        print(f"❌ Error: {e}")
        # Optional: Send yourself an error log so you know it crashed
        # send_alert(f"Bot crashed: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    check_changi()
