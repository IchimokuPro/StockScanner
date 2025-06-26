# Stock Scanner with Volume & OI Spurt Detection

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Stock Screener - Volume & OI Spurt", layout="wide")
st.title("📊 Stock Screener - Volume & OI Spurt Detector")

# ------------------- OI Buildup Scraper -------------------
@st.cache_data(ttl=600)
def fetch_oi_buildup():
    url = "https://www.moneycontrol.com/stocks/marketstats/futures/oi-spurts/fno/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        page = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(page.content, "html5lib")
        tables = pd.read_html(str(soup))
        if tables:
            df = tables[0]
            expected_cols = ["Stock", "Price", "Chg %", "OI"]  # Expect 4 columns
            if len(df.columns) == len(expected_cols):
                df.columns = expected_cols
                return df
            elif len(df.columns) >= 7:
                df.columns = ["Stock", "Price", "Chg %", "OI", "OI Chg %", "Vol", "Vol Chg %"]
                return df
            else:
                st.warning(f"⚠️ Column mismatch! Expected 4 or 7 columns but got {len(df.columns)}")
                st.write("Raw columns:", df.columns.tolist())
                return pd.DataFrame()
        else:
            raise ValueError("No tables found on OI page")
    except Exception as e:
        st.error(f"⚠️ Error fetching OI data: {e}")
        return pd.DataFrame()

# ------------------- Unusual Volume Scraper -------------------
@st.cache_data(ttl=600)
def fetch_unusual_volume():
    url = "https://www.tradingview.com/markets/stocks-india/market-movers-unusual-volume/"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}  # avoid bot detection
        page = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(page.content, "html.parser")
        table_rows = soup.select(".tv-data-table__tbody tr")
        data = []
        for row in table_rows:
            cols = row.find_all("td")
            if len(cols) >= 6:
                stock = cols[0].text.strip()
                price = cols[1].text.strip()
                chg = cols[2].text.strip()
                vol_rel = cols[5].text.strip()
                data.append({"Stock": stock, "Price": price, "Change": chg, "Rel Volume": vol_rel})
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"⚠️ Error fetching volume data: {e}")
        return pd.DataFrame()

# ------------------- Main App -------------------
st.sidebar.header("🔍 Scanner Options")
if st.sidebar.button("🚀 Refresh Data"):
    with st.spinner("Fetching latest data..."):
        st.session_state["oi"] = fetch_oi_buildup()
        st.session_state["vol"] = fetch_unusual_volume()
        st.success("Data refreshed!")

st.subheader("📈 Open Interest Spurts")
if "oi" in st.session_state and not st.session_state["oi"].empty:
    st.dataframe(st.session_state["oi"], use_container_width=True)
else:
    st.info("Click 'Refresh Data' to load OI spurts.")

st.subheader("📊 Unusual Volume Movers")
if "vol" in st.session_state and not st.session_state["vol"].empty:
    st.dataframe(st.session_state["vol"], use_container_width=True)
else:
    st.info("Click 'Refresh Data' to load unusual volume movers.")
