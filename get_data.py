from datetime import datetime
import pandas as pd
from mongo_connector import get_db
import streamlit as st

def load_intraday_data(symbol):
    db = get_db()
    collection = db["psx_intraday"]
    results = collection.find({"ticker": symbol})
    all_data = []
    for doc in results:
        for row in doc.get("data", []):
            try:
                timestamp_unix, price, volume = row
                dt = datetime.utcfromtimestamp(timestamp_unix)
                all_data.append({
                    "timestamp": dt,
                    "price": price,
                    "volume": volume
                })
            except Exception as e:
                print(f"Error parsing row {row} for {symbol}: {e}")
    return pd.DataFrame(all_data)

def show_intraday_chart(symbol):
    df = load_intraday_data(symbol)
    if df.empty:
        st.warning("No intraday data found.")
        return

    df = df.sort_values("timestamp")
    st.subheader("📈 Intraday Price Chart")
    st.line_chart(df.set_index("timestamp")[["price"]], height=300, use_container_width=True)

    st.subheader("📊 Volume Chart")
    st.bar_chart(df.set_index("timestamp")[["volume"]], height=200, use_container_width=True)
