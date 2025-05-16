fastapi
uvicorn
requests
python-multipart
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")'  # Do NOT hardcode this in production. Use env variables!

def get_stock_price(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

def get_stock_news(symbol):
    today = datetime.date.today().isoformat()
    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={today}&to={today}&token={FINNHUB_API_KEY}"
    r = requests.get(url)
    return r.json() if r.status_code == 200 else []

@app.get("/screener")
def screener():
    symbols = ["IMPP", "SNDL", "BBIG", "GROM", "SOFI"]
    results = []

    for symbol in symbols:
        quote = get_stock_price(symbol)
        if not quote or quote.get("c") == 0:
            continue

        try:
            current_price = quote["c"]
            previous_close = quote["pc"]
            gap = round(((current_price - previous_close) / previous_close) * 100, 2)

            mock_float = 8000000
            mock_volume = 5.5

            if 2 <= current_price <= 20 and gap >= 10 and mock_float < 10_000_000:
                news = get_stock_news(symbol)
                headline = news[0]["headline"] if news else "None"
                results.append({
                    "symbol": symbol,
                    "price": current_price,
                    "gap": gap,
                    "volume": mock_volume,
                    "float": mock_float,
                    "news": headline
                })

        except Exception:
            continue

    return results
