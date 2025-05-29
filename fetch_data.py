import requests
from datetime import datetime
from mongo_connector import get_db  # This is the MongoDB utility from earlier

def fetch_tickers_metadata():
    response = requests.get("https://dps.psx.com.pk/symbols")
    if response.status_code != 200:
        return None
    return response.json()

def fetch_data(ticker):
    response = requests.get(f"https://dps.psx.com.pk/timeseries/int/{ticker}")
    if response.status_code != 200:
        return None
    return response.json()

def filter_symbols(tickers_object_list):
    return [t['symbol'] for t in tickers_object_list if not t.get('isDebt', True)]

def fetch_and_store_all():
    db = get_db()
    collection = db["psx_intraday"]

    tickers_metadata = fetch_tickers_metadata()
    if not tickers_metadata:
        print("Failed to fetch metadata.")
        return

    ticker_symbols = filter_symbols(tickers_metadata)

    timestamp = datetime.utcnow()  # Use UTC for standard timestamping

    for ticker in ticker_symbols:
        data = fetch_data(ticker)
        if data and data.get('status') == 1:
            doc = {
                "ticker": ticker,
                "timestamp": timestamp,
                "data": data["data"]
            }
            collection.insert_one(doc)
            print(f"Stored data for {ticker}")
        else:
            print(f"Failed to fetch data for {ticker}")

fetch_and_store_all()
