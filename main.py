import os
import requests
from time import sleep
from bs4 import BeautifulSoup
import streamlit as st
from pymongo import MongoClient
from get_data import show_intraday_chart
import base64

BASE_URL = "https://dps.psx.com.pk"
HEADERS = {"User-Agent": "Mozilla/5.0"}
DOWNLOAD_DIR = "contents"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "PSX_datacentre"
COLLECTION_NAME = "pdf_metadata"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def fetch_metadata():
    url = f"{BASE_URL}/symbols"
    response = requests.get(url, headers=HEADERS)
    sleep(2)
    if response.status_code != 200:
        return []
    return response.json()

def get_stock_url(entry):
    symbol = entry.get("symbol")
    position = "debt" if entry.get("isDebt") else "company"
    return f"{BASE_URL}/{position}/{symbol}"

def fetch_stock_page(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return None
    return response.text

def parse_and_download_pdfs(html, symbol):
    soup = BeautifulSoup(html, "html.parser")
    pdfs = []
    links = soup.find_all("a", href=lambda href: href and ".pdf" in href)
    for a in links:
        href = a["href"]
        full_url = BASE_URL + href
        filename = href.split("/")[-1]
        local_path = os.path.join(DOWNLOAD_DIR, filename)
        if not os.path.exists(local_path):
            try:
                pdf_res = requests.get(full_url, headers=HEADERS)
                if pdf_res.status_code == 200:
                    with open(local_path, "wb") as f:
                        f.write(pdf_res.content)
                else:
                    continue
            except:
                continue
        tr = a.find_parent("tr")
        td_texts = [td.get_text(strip=True) for td in tr.find_all("td")] if tr else []
        entry_data = {
            "symbol": symbol,
            "filename": filename,
            "url": full_url,
            "local_path": local_path,
            "meta": {
                "date": td_texts[0] if len(td_texts) > 0 else None,
                "description": td_texts[1] if len(td_texts) > 1 else None
            }
        }
        if not collection.find_one({"symbol": symbol, "filename": filename}):
            collection.insert_one(entry_data)
        pdfs.append(entry_data)
    return pdfs

def display_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="PSX_Analyzer", page_icon="😎", layout="wide")
    st.title("😎 Abdul Ghani's PSX Analyzer Dashboard")
    metadata = fetch_metadata()
    if not metadata:
        st.stop()
    options = {f"{item['symbol']} - {item['name']}": item for item in metadata}
    selected_key = st.selectbox("🔍 Select by symbol or name", options.keys())
    selected_entry = options[selected_key]
    symbol = selected_entry["symbol"]
    st.subheader(f"{symbol} — {selected_entry['name']}")
    stock_url = get_stock_url(selected_entry)
    st.markdown(f"[🔗 Open Stock Page]({stock_url})")
    html = fetch_stock_page(stock_url)
    if not html:
        st.error("Failed to load stock page.")
        return
    pdf_entries = parse_and_download_pdfs(html, symbol)
    if not pdf_entries:
        st.warning("No PDF documents found.")
        return
    st.markdown(f"### 📁 Local PDFs ({len(pdf_entries)})")
    for entry in pdf_entries:
        with st.expander(f"📄 {entry['meta']['description'] or entry['filename']}"):
            st.write("🗓️ Date:", entry['meta']['date'] or "N/A")
            st.write("📝 Description:", entry['meta']['description'] or "N/A")
            if st.button(f"View PDF - {entry['filename']}"):
                display_pdf(entry["local_path"])
    st.markdown("### 📊 Intraday Data from Database")
    show_intraday_chart(symbol)

if __name__ == "__main__":
    main()
