import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. CONFIGURATION ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_alert(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Telegram keys are missing!")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

# --- 2. BROWSER SETUP ---
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# --- 3. THE SCRAPER ---
def check_changi():
    driver = get_driver()
    print("🚀 Launching cloud browser...")
    
    try:
        driver.get("https://www.changiairport.com/en/flights/arrivals.html")
        print("⏳ Waiting 15 seconds for flight list...")
        time.sleep(15) 
        
        flights = driver.find_elements(By.CLASS_NAME, "flightlist__item")
        count = len(flights)
        print(f"🔎 Found {count} flights.")

        if count > 0:
            msg = f"✈️ **Airport Update** ({count} flights found)\n"
            msg += "-----------------------------\n"
            
            # Show first 8 flights now (increased from 5)
            for i, flight in enumerate(flights[:8]):
                try:
                    time_val = flight.find_element(By.CLASS_NAME, "flightlist__item-time").text.replace('\n', ' ')
                    flight_num = flight.find_element(By.CLASS_NAME, "airport__flight-number").text
                    terminal = flight.find_element(By.CLASS_NAME, "flightlist__item-terminal").text
                    
                    # --- THE FIX IS HERE ---
                    # Removed the "T" before {terminal}
                    msg += f"• *{time_val}* | {flight_num} ({terminal})\n"
                except:
                    continue
            
            msg += "\n🚗 *Check apps for surge!*"
            send_alert(msg)
            print("✅ Telegram alert sent!")
            
        else:
            print("⚠️ List is empty.")

    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    check_changi()
