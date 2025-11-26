# backend.py
import os
import logging
from aiohttp import web
import asyncio
from datetime import datetime, timezone, timedelta
import requests

# ============================
# Timezone: Nigeria UTC+1
# ============================
NIGERIA_TZ = timezone(timedelta(hours=1))

# ============================
# Logging configuration
# ============================
LOGFILE = "backend.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOGFILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================
# Backend web app
# ============================
app = web.Application()

# Default pairs
PAIRS = ["EUR/USD", "AUD/USD"]

# In-memory store
price_data = {pair: [] for pair in PAIRS}
signal_data = {pair: {} for pair in PAIRS}

# ============================
# Routes
# ============================
async def health(request):
    return web.json_response({"status": "ok"})

async def price(request):
    pair = request.query.get("pair")
    if pair not in price_data:
        return web.Response(status=404, text="Pair not found")
    return web.json_response({"meta": {"symbol": pair}, "values": price_data[pair]})

async def signal(request):
    pair = request.query.get("pair")
    if pair not in signal_data:
        return web.Response(status=404, text="Pair not found")
    return web.json_response(signal_data[pair])

app.add_routes([
    web.get("/health", health),
    web.get("/price", price),
    web.get("/signal", signal)
])

# ============================
# Poller to update mock prices
# Replace with real API call if needed
# ============================
async def poller():
    while True:
        now = datetime.now(NIGERIA_TZ).strftime("%Y-%m-%d %H:%M:%S")
        for pair in PAIRS:
            # Example: random price update
            last_close = price_data[pair][-1]["close"] if price_data[pair] else 1.1565
            open_price = last_close
            close_price = round(open_price + 0.0001, 5)
            price_data[pair].append({
                "datetime": now,
                "open": open_price,
                "close": close_price
            })
            # Generate simple signal
            signal_data[pair] = {
                "pair": pair,
                "signal": "BUY" if close_price >= open_price else "SELL",
                "open": open_price,
                "close": close_price,
                "datetime": now
            }
        logger.info(f"Updated prices and signals at {now}")
        await asyncio.sleep(60)  # fetch every minute

# ============================
# Run app
# ============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    loop = asyncio.get_event_loop()
    loop.create_task(poller())
    web.run_app(app, host="0.0.0.0", port=port)
