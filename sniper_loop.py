# sniper_loop.py
import os
import time
import requests
from datetime import datetime, timezone, timedelta

# ============================
# Configuration
# ============================
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8080")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
PAIRS = ["EUR/USD", "AUD/USD"]

# Nigeria timezone
NIGERIA_TZ = timezone(timedelta(hours=1))

def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code != 200:
            print(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def fetch_signal(pair: str):
    try:
        response = requests.get(f"{BACKEND_URL}/signal", params={"pair": pair}, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching {pair}: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error fetching {pair}: {e}")
    return None

def main():
    print(f"Starting SNIPER loop (Nigeria Time UTC+1)...")
    while True:
        for pair in PAIRS:
            signal = fetch_signal(pair)
            if signal:
                dt = signal.get("datetime")
                s = signal.get("signal")
                message = f"Sent signal: {pair} – {s} at {dt}"
                print(message)
                send_telegram(message)
        time.sleep(60)  # check every minute

if __name__ == "__main__":
    main()
