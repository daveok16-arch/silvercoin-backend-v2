import os
import time
import requests
from datetime import datetime, timezone, timedelta

# ============================
# Timezone: Nigeria UTC+1
# ============================
NIGERIA_TZ = timezone(timedelta(hours=1))

# ============================
# Environment variables
# ============================
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8080")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise RuntimeError("Telegram credentials not set in environment")

# ============================
# Default pairs
# ============================
pair_list = ["EUR/USD", "AUD/USD", "GBP/USD", "USD/JPY"]

# ============================
# Helper functions
# ============================
def fetch_signal(pair):
    """Fetch signal from backend for a pair"""
    try:
        resp = requests.get(f"{BACKEND_URL}/signal", params={"pair": pair}, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"Error fetching {pair}: {e}")
        return None

def send_telegram(message):
    """Send Telegram message"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

# ============================
# Main loop
# ============================
def main_loop():
    print(f"Starting SNIPER loop (Nigeria Time UTC+1)...")
    while True:
        for pair in pair_list:
            signal = fetch_signal(pair)
            if signal:
                print(f"{datetime.now(NIGERIA_TZ)} - {pair}: {signal['signal']}")
                send_telegram(f"{pair} signal: {signal['signal']}")
        time.sleep(60)  # Run every minute

# ============================
# Run
# ============================
if __name__ == "__main__":
    main_loop()
