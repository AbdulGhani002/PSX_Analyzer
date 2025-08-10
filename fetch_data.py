import requests
from datetime import datetime
from datetime import datetime, UTC
from mongo_connector import get_db

def fetch_tickers_metadata():
    res = requests.get("https://dps.psx.com.pk/symbols")
    if res.status_code != 200:
        return None
    return res.json()

def fetch_data(ticker):
    res = requests.get(f"https://dps.psx.com.pk/timeseries/int/{ticker}")
    if res.status_code != 200:
        return None
    return res.json()

def filter_symbols(tickers_list):
    return [t['symbol'] for t in tickers_list if not t.get('isDebt', True)]


def fetch_and_store_all():
    db = get_db()
    collection = db["psx_intraday"]

    tickers_metadata = fetch_tickers_metadata()
    if not tickers_metadata:
        print("❌ Failed to fetch metadata.")
        return

    ticker_symbols = filter_symbols(tickers_metadata)

    for ticker in ticker_symbols:
        data_json = fetch_data(ticker)

        if not data_json or data_json.get("status") != 1:
            print(f"⚠️ No data for {ticker}")
            continue

        api_data = data_json["data"]

        # Get last stored timestamp but only if data array exists and is non-empty
        latest_doc = collection.find_one(
            {"ticker": ticker, "data.0": {"$exists": True}},
            sort=[("data.0.0", -1)]
        )

        latest_ts_db = None
        if latest_doc and latest_doc.get("data"):
            latest_ts_db = latest_doc["data"][-1][0]  # last entry's timestamp

        # Filter only new data
        if latest_ts_db is not None:
            api_data = [row for row in api_data if row[0] > latest_ts_db]

        if not api_data:
            print(f"⏩ No new intraday points for {ticker}")
            continue

        collection.insert_one({
            "ticker": ticker,
            "fetched_at": datetime.now(UTC), 
            "data": api_data
        })
        print(f"✅ Stored {len(api_data)} new points for {ticker}")


fetch_and_store_all()
