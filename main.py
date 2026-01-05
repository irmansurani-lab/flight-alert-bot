import os
import time
import requests
from collections import Counter
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
        
        # Get all rows
        raw_rows = driver.find_elements(By.CLASS_NAME, "flightlist__item")
        
        valid_flights = []
        terminals = []

        # Process rows to remove empty ones
        for row in raw_rows:
            try:
                flight_num = row.find_element(By.CLASS_NAME, "airport__flight-number").text.strip()
                if not flight_num: 
                    continue 

                time_val = row.find_element(By.CLASS_NAME, "flightlist__item-time").text.replace('\n', ' ')
                
                # The website gives us "T1", "T2", etc.
                terminal = row.find_element(By.CLASS_NAME, "flightlist__item-terminal").text.strip()
                
                # CLEANER LIST FORMAT: Removed the extra 'T' here
                valid_flights.append(f"• *{time_val}* {flight_num} ({terminal})")
                terminals.append(terminal)
            except:
                continue 

        count = len(valid_flights)
        print(f"🔎 Found {count} VALID flights.")

        if count > 0:
            # --- LOGIC: Find the Busiest Terminal ---
            t_counts = Counter(terminals)
            # e.g., best_terminal will be "T1"
            best_terminal = t_counts.most_common(1)[0][0] 
            
            # --- BUILD THE MESSAGE ---
            msg = f"🚕 **Driver Strategy Update**\n"
            msg += f"Found {count} flights landing.\n\n"
            
            # CLEANER HEADER: Removed extra 'T's
            msg += f"🔥 **GO TO TERMINAL {best_terminal}**\n"
            msg += f"_({best_terminal} has {t_counts[best_terminal]} incoming flights)_\n"
            msg += "-----------------------------\n"
            msg += "_Showing next 8 arrivals:_\n" # Added clarification
            
            # Show top 8 flights
            msg += "\n".join(valid_flights[:8])
            
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
