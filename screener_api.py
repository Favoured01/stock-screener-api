import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import datetime
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Stock Screener API is live!"}

# Load API Key from environment variable
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
# Do NOT hardcode this in production. Use env variables!

def get_stock_price(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

def get_stock_news(symbol):
    today = datetime.date.today().isoformat()
    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={today}&to={today}&token={FINNHUB_API_KEY}"
    r = requests.get(url)
    return r.json() if r.status_code == 200 else []

class SymbolRequest(BaseModel):
    symbols: List[str]

@app.post("/screen")
async def screen_stocks(request: SymbolRequest):
    results = []

    for symbol in request.symbols:
        try:
            quote = get_stock_price(symbol)
            if not quote or "c" not in quote or "pc" not in quote:
                continue

            current_price = quote["c"]
            previous_close = quote["pc"]
            gap = round(((current_price - previous_close) / previous_close) * 100, 2)

            # Mock data
            mock_float = 8000000
            mock_volume = 5.5
            avg_volume = 9000000

            volume_spike = mock_volume > 1.5 * avg_volume

            if current_price > 0 and volume_spike:
                news = get_stock_news(symbol)
                headline = news[0]["headline"] if news else "None"
                results.append({
                    "symbol": symbol,
                    "price": current_price,
                    "gap": gap,
                    "volume": mock_volume,
                    "avg_volume": avg_volume,
                    "float": mock_float,
                    "volume_spike": volume_spike,
                    "news": headline
                })

        except Exception:
            continue

    return {"results": results}
