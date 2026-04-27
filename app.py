import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

st.title("🚀 V3 Execution Engine (FIXED ALERT SYSTEM)")

# -----------------------------
# INPUTS
# -----------------------------
user_tickers = st.text_input(
    "➕ Add extra tickers (comma separated)",
    "GME,AMC,TSLA"
)

refresh_rate = st.slider("Refresh interval (seconds)", 5, 60, 10)
start = st.toggle("🟢 Start Engine")

# -----------------------------
# UNIVERSE
# -----------------------------
def get_full_universe():
    return [
        "AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA","JPM",
        "V","XOM","PG","MA","HD","CVX","PEP","KO","WMT","BAC",
        "PLTR","GME","AMC","BB","NIO","SOFI","RIVN","LCID",
        "AMD","INTC","PYPL","UBER","SQ","SHOP","BABA"
    ]

def merge_universe(user_input):
    universe = get_full_universe()
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

if "last_alert" not in st.session_state:
    st.session_state.last_alert = {}

cooldown = 180  # shorter so you actually see alerts
placeholder = st.empty()

# -----------------------------
# ENGINE
# -----------------------------
if start:

    now = time.time()

    # -----------------------------
    # SCAN
    # -----------------------------
    if now - st.session_state.last_run >= refresh_rate:

        tickers = merge_universe(user_tickers)[:120]
        results = []

        for t in tickers:
            try:
                res = check_signal(t)
                if res:
                    results.append(res)
            except Exception as e:
                print("[SCAN ERROR]", t, e)

        results.sort(key=lambda x: x.get("score", 0), reverse=True)

        st.session_state.cache = results
        st.session_state.last_run = now

    results = st.session_state.cache

    # -----------------------------
    # UI
    # -----------------------------
    with placeholder.container():

        st.subheader("📊 Market Radar")

        if not results:
            st.info("Scanning market...")
            st.stop()

        st.dataframe(results)

        st.subheader("🚀 V3 LIVE EXECUTION SIGNALS")

        for r in results:

            ticker = r.get("ticker")
            price = r.get("price", 0)

            setup = r.get("setup_score", 0)
            squeeze = r.get("squeeze_score", 0)
            trade = r.get("trade") or {}

            entry_low, entry_high = trade.get("entry", (0, 0))
            stop = trade.get("stop", 0)
            t1 = trade.get("target1", 0)
            t2 = trade.get("target2", 0)
            rr = trade.get("rr", 0)
            state = trade.get("state", "WAITING")

            msg = (
                f"{ticker} | ${price}\n"
                f"STATE: {state}\n"
                f"ENTRY {entry_low}-{entry_high}\n"
                f"STOP {stop} | T1 {t1} | T2 {t2}\n"
                f"RR {rr} | Setup {setup}% | Squeeze {squeeze}%"
            )

            last_time = st.session_state.last_alert.get(ticker, 0)

            # -----------------------------
            # CORE ALERT CONDITIONS (FIXED LOGIC)
            # -----------------------------
            is_entry_zone = entry_low <= price <= entry_high
            is_breakout = price > entry_high
            is_extreme = setup >= 80 and rr >= 1.5
            is_strong = setup >= 65 and squeeze >= 55

            should_alert = (
                is_extreme or
                (is_strong and is_entry_zone) or
                (is_breakout and rr >= 1.3)
            )

            # -----------------------------
            # ALERT ENGINE (FIXED)
            # -----------------------------
            if should_alert:

                if now - last_time > cooldown:

                    if is_extreme:
                        alert_msg = "🔥 EXTREME EXECUTION SETUP: " + msg
                        st.error(alert_msg)
                    elif is_breakout:
                        alert_msg = "🚀 BREAKOUT ALERT: " + msg
                        st.warning(alert_msg)
                    else:
                        alert_msg = "⚡ ENTRY ALERT: " + msg
                        st.success(alert_msg)

                    # 🔥 CRITICAL: show telegram result
                    result = send_alert(alert_msg)
                    st.write(f"📡 TELEGRAM RESULT {ticker}: {result}")

                    st.session_state.last_alert[ticker] = now

            # -----------------------------
            # DISPLAY
            # -----------------------------
            if state == "WAITING":
                st.info(msg)
            else:
                st.warning(msg)

        # -----------------------------
        # TOP 10
        # -----------------------------
        st.subheader("🏆 Top 10")

        for r in results[:10]:
            trade = r.get("trade") or {}
            st.write(
                f"{r['ticker']} | ${r['price']} | "
                f"RR {trade.get('rr', 0)} | "
                f"STATE {trade.get('state', 'WAITING')}"
            )
