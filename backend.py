import os
import logging
from aiohttp import web
import asyncio
from datetime import datetime, timezone, timedelta

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
PAIRS = ["EUR/USD", "AUD/USD", "GBP/USD", "USD/JPY"]

# In-memory stores
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
        return web.Response(status=404, text="Not Found")
    return web.json_response({"meta": {"symbol": pair}, "values": price_data[pair]})

async def signal(request):
    pair = request.query.get("pair")
    if pair not in signal_data:
        return web.Response(status=404, text="Not Found")
    return web.json_response(signal_data[pair])

app.add_routes([
    web.get("/health", health),
    web.get("/price", price),
    web.get("/signal", signal)
])

# ============================
# Poller to fetch mock data (replace with real API)
# ============================
async def poller():
    while True:
        now = datetime.now(NIGERIA_TZ).strftime("%Y-%m-%d %H:%M:%S")
        for pair in PAIRS:
            # Mock price fetch logic
            open_price = round(1.150 + 0.01 * hash(pair) % 0.01, 5)
            close_price = round(open_price + 0.0005, 5)
            price_data[pair].append({
                "datetime": now,
                "open": open_price,
                "close": close_price
            })
            signal_data[pair] = {
                "pair": pair,
                "signal": "BUY" if close_price > open_price else "SELL",
                "open": open_price,
                "close": close_price,
                "datetime": now
            }
        logger.info(f"Updated prices and signals at {now}")
        await asyncio.sleep(60)  # every minute

# ============================
# Run app
# ============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    loop = asyncio.get_event_loop()
    loop.create_task(poller())
    web.run_app(app, host="0.0.0.0", port=port)
