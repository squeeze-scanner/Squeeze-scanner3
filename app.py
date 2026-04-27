import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

st.title("🚀 V4 Execution Engine (STABLE CORE)")

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
# STATE (V4 CORE FIX)
# -----------------------------
if "cache" not in st.session_state:
    st.session_state.cache = []

if "last_alert" not in st.session_state:
    st.session_state.last_alert = {}

if "last_state" not in st.session_state:
    st.session_state.last_state = {}

if "last_run" not in st.session_state:
    st.session_state.last_run = 0

cooldown = 120
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
            except:
                continue

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

        st.subheader("🚀 V4 EXECUTION ENGINE")

        for r in results:

            ticker = r.get("ticker")
            price = r.get("price", 0)

            setup = r.get("setup_score", 0)
            squeeze = r.get("squeeze_score", 0)

            trade = r.get("trade_plan", {})

            entry_low, entry_high = trade.get("entry", (0, 0))
            stop = trade.get("stop", 0)
            t1 = trade.get("target1", 0)
            t2 = trade.get("target2", 0)
            rr = trade.get("rr", 0)

            # -----------------------------
            # STATE MEMORY (CRITICAL FIX)
            # -----------------------------
            prev_state = st.session_state.last_state.get(ticker, "NONE")

            if entry_low <= price <= entry_high:
                state = "ENTRY"
            elif price > entry_high and entry_high > 0:
                state = "BREAKOUT"
            else:
                state = "WAITING"

            st.session_state.last_state[ticker] = state

            msg = (
                f"{ticker} | ${price}\n"
                f"STATE {state}\n"
                f"ENTRY {entry_low}-{entry_high}\n"
                f"STOP {stop} | T1 {t1} | T2 {t2}\n"
                f"RR {rr} | Setup {setup}% | Squeeze {squeeze}%"
            )

            last_time = st.session_state.last_alert.get(ticker, 0)

            # -----------------------------
            # ALERT CONDITIONS (V4 CLEAN)
            # -----------------------------
            is_new_state = state != prev_state

            is_strong = setup >= 60 and squeeze >= 50
            is_extreme = setup >= 80 and rr >= 1.3

            should_alert = (
                is_new_state and (
                    is_extreme or
                    (is_strong and state == "ENTRY") or
                    state == "BREAKOUT"
                )
            )

            # -----------------------------
            # ALERT EXECUTION
            # -----------------------------
            if should_alert and now - last_time > cooldown:

                if is_extreme:
                    alert_msg = "🔥 EXTREME SETUP: " + msg
                    st.error(alert_msg)

                elif state == "BREAKOUT":
                    alert_msg = "🚀 BREAKOUT ALERT: " + msg
                    st.warning(alert_msg)

                else:
                    alert_msg = "⚡ ENTRY ALERT: " + msg
                    st.success(alert_msg)

                result = send_alert(alert_msg)

                st.write("📡 TELEGRAM:", result)

                st.session_state.last_alert[ticker] = now

            st.info(msg)

        # -----------------------------
        # TOP 10
        # -----------------------------
        st.subheader("🏆 Top 10")

        for r in results[:10]:
            trade = r.get("trade_plan", {})
            st.write(
                f"{r['ticker']} | ${r['price']} | RR {trade.get('rr', 0)}"
            )
