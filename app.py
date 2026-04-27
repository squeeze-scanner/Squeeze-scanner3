import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

# -----------------------------
# TITLE
# -----------------------------
st.title("🚀 V20 Full Market Scanner (Stable Mode)")

# -----------------------------
# USER INPUT
# -----------------------------
user_tickers = st.text_input(
    "➕ Add extra tickers (comma separated)",
    "GME,AMC,TSLA"
)

refresh_rate = st.slider("Refresh interval (seconds)", 5, 60, 10)
start = st.toggle("🟢 Start Scanner")

# -----------------------------
# EXTENDED UNIVERSE (REALISTIC BROAD MARKET SET)
# -----------------------------
def get_full_universe():
    base = [
        "AAPL","MSFT","NVDA","AMZN","META","GOOGL","GOOG","TSLA","BRK-B","JPM",
        "V","UNH","XOM","PG","MA","HD","CVX","LLY","ABBV","AVGO",
        "PEP","COST","MRK","KO","WMT","BAC","DIS","ADBE","NFLX","CRM"
    ]

    momentum = [
        "PLTR","GME","AMC","BB","NIO","SOFI","RIVN","LCID","COIN",
        "AMD","INTC","PYPL","UBER","LYFT","SQ","SHOP","BABA","BA",
        "ORCL","T","VZ","INTU"
    ]

    return list(set(base + momentum))

def merge_universe(user_input):
    universe = get_full_universe()

    if user_input:
        manual = [t.strip().upper() for t in user_input.split(",") if t.strip()]
        universe.extend(manual)

    return list(set(universe))

# -----------------------------
# SESSION STATE
# -----------------------------
if "cache" not in st.session_state:
    st.session_state.cache = []

if "last_run" not in st.session_state:
    st.session_state.last_run = 0

if "last_alert" not in st.session_state:
    st.session_state.last_alert = {}

placeholder = st.empty()

cooldown = 600  # prevent spam alerts

# -----------------------------
# MAIN LOOP
# -----------------------------
if start:

    now = time.time()

    # only run scan every X seconds
    if now - st.session_state.last_run >= refresh_rate:

        tickers = merge_universe(user_tickers)

        results = []

        # -----------------------------
        # SCAN ENGINE
        # -----------------------------
        for t in tickers:
            try:
                res = check_signal(t)
                if res:
                    results.append(res)
            except:
                continue

        # sort by score
        results.sort(key=lambda x: x.get("score", 0), reverse=True)

        st.session_state.cache = results
        st.session_state.last_run = now

    results = st.session_state.cache

    # -----------------------------
    # UI RENDER
    # -----------------------------
    with placeholder.container():

        st.subheader("📊 Market Radar")

        st.write(f"Scanning {len(merge_universe(user_tickers))} tickers")

        if results:

            st.dataframe(results)

            st.subheader("🚨 Alerts")

            for r in results:

                ticker = r.get("ticker")
                signal = r.get("signal")
                score = r.get("score")
                price = r.get("price")

                msg = f"{ticker} | {signal} | Score {score} | ${price}"

                last_time = st.session_state.last_alert.get(ticker, 0)

                # -----------------------------
                # ALERT LOGIC
                # -----------------------------
                if signal == "HIGH":

                    if now - last_time > cooldown:
                        st.error("🔥 " + msg
