import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

# -----------------------------
# TITLE
# -----------------------------
st.title("🚀 V20 Full Market Autonomous Scanner")

# -----------------------------
# INPUT BAR (NEW FEATURE)
# -----------------------------
user_tickers = st.text_input(
    "➕ Add extra tickers (optional)",
    "GME,AMC,TSLA"
)

refresh_rate = st.slider("Refresh interval (seconds)", 5, 60, 10)

start = st.toggle("🟢 Start Full Market Scan")

# -----------------------------
# FULL MARKET UNIVERSE
# -----------------------------
BASE_UNIVERSE = [
    "AAPL","MSFT","NVDA","TSLA","AMZN","META","GOOGL","GOOG",
    "PLTR","GME","AMC","BB","NIO","SOFI","RIVN","LCID","COIN",
    "AMD","INTC","NFLX","PYPL","UBER","LYFT","SQ","SHOP",
    "SPY","QQQ","IWM","DIA","ARKK",
    "BABA","BA","DIS","ORCL","CRM","T","V","MA","JPM","GS"
]

def get_universe(user_input):
    universe = BASE_UNIVERSE.copy()

    if user_input:
        manual = [t.strip().upper() for t in user_input.split(",") if t.strip()]
        universe.extend(manual)

    return list(set(universe))

# -----------------------------
# STATE
# -----------------------------
if "cache" not in st.session_state:
    st.session_state.cache = []

if "last_run" not in st.session_state:
    st.session_state.last_run = 0

placeholder = st.empty()

# -----------------------------
# MAIN ENGINE
# -----------------------------
if start:

    now = time.time()

    if now - st.session_state.last_run > refresh_rate:

        tickers = get_universe(user_tickers)

        results = []

        # FULL SCAN
        for t in tickers:
            try:
                res = check_signal(t)
                if res:
                    results.append(res)
            except:
                pass

        # rank
        results.sort(key=lambda x: x.get("score", 0), reverse=True)

        st.session_state.cache = results
        st.session_state.last_run = now

    results = st.session_state.cache

    # -----------------------------
    # UI
    # -----------------------------
    with placeholder.container():

        st.subheader("📊 Full Market Radar")

        st.write(f"Scanning {len(get_universe(user_tickers))} tickers")

        if results:

            st.dataframe(results)

            st.subheader("🚨 Alerts")

            for r in results:

                msg = f"{r['ticker']} | {r['signal']} | {r['score']} | ${r.get('price')}"

                if r["signal"] == "HIGH":
                    st.error("🔥 " + msg)
                    send_alert("🔥 " + msg)

                elif r["signal"] == "MED":
                    st.warning("⚠️ " + msg)

            st.subheader("🏆 Top 10")

            for r in results[:10]:
                st.write(
                    f"{r['ticker']} → {r['signal']} | "
                    f"${r.get('price')} | Score {r.get('score')}"
                )

        else:
            st.info("Scanning full market...")

    time.sleep(1)
    st.rerun()
