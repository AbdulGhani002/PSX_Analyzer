import os
import requests
from time import sleep
from bs4 import BeautifulSoup
import streamlit as st

BASE_URL = "https://dps.psx.com.pk"
HEADERS = {"User-Agent": "Mozilla/5.0"}
DOWNLOAD_DIR = "contents"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def fetch_metadata():
    """Fetch PSX symbol metadata"""
    url = f"{BASE_URL}/symbols"
    response = requests.get(url, headers=HEADERS)
    sleep(2)
    if response.status_code != 200:
        print("❌ Failed to fetch metadata")
        return []
    return response.json()


def get_stock_url(entry):
    """Build stock page URL from entry"""
    symbol = entry.get("symbol")
    position = "debt" if entry.get("isDebt") else "company"
    return f"{BASE_URL}/{position}/{symbol}"


def fetch_stock_page(url):
    """Fetch HTML content of a stock's page"""
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print("❌ Failed to load stock page:", url)
        return None
    return response.text


def parse_and_download_pdfs(html):
    """Extract PDF links, download them, and return metadata"""
    soup = BeautifulSoup(html, "html.parser")
    pdfs = []

    links = soup.find_all("a", href=lambda href: href and ".pdf" in href)
    for a in links:
        href = a["href"]
        full_url = BASE_URL + href
        filename = href.split("/")[-1]
        local_path = os.path.join(DOWNLOAD_DIR, filename)

        # Downloading if not exist
        if not os.path.exists(local_path):
            try:
                pdf_res = requests.get(full_url, headers=HEADERS)
                if pdf_res.status_code == 200:
                    with open(local_path, "wb") as f:
                        f.write(pdf_res.content)
                    print(f"✅ Downloaded: {filename}")
                else:
                    print(f"❌ Failed to download: {full_url}")
            except Exception as e:
                print(f"⚠️ Error downloading {full_url}: {e}")
                continue
        else:
            print(f"📁 Already exists: {filename}")

        # Parsing table row metadata
        tr = a.find_parent("tr")
        td_texts = [td.get_text(strip=True) for td in tr.find_all("td")] if tr else []

        pdfs.append({
            "filename": filename,
            "local_path": local_path,
            "meta": td_texts,
        })

    return pdfs


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

    pdf_entries = parse_and_download_pdfs(html)

    if not pdf_entries:
        st.warning("No PDF documents found.")
        return

    st.markdown(f"### 📁 Local PDFs ({len(pdf_entries)})")
    for entry in pdf_entries:
        with st.expander(f"📄 {entry['meta'][1] if len(entry['meta']) > 1 else entry['filename']}"):
            st.write("🗓️ Date:", entry['meta'][0] if len(entry['meta']) > 0 else "N/A")
            st.write("📝 Description:", entry['meta'][1] if len(entry['meta']) > 1 else "N/A")

            # Streamlit-safe file URL (must be inside app dir)
            rel_path = os.path.join(DOWNLOAD_DIR, entry["filename"])
            st.markdown(f"[📥 Open PDF]({rel_path})")


if __name__ == "__main__":
    main()
