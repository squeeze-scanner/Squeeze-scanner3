import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

st.title("🚀 V3 Execution Engine (LIVE TRADE TRACKER)")

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

if "active_trades" not in st.session_state:
    st.session_state.active_trades = {}

if "last_run" not in st.session_state:
    st.session_state.last_run = 0

if "last_alert" not in st.session_state:
    st.session_state.last_alert = {}

cooldown = 300
placeholder = st.empty()


# -----------------------------
# MAIN ENGINE
# -----------------------------
if start:

    now = time.time()

    # -----------------------------
    # SCAN ENGINE
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

        st.subheader("🚀 V3 LIVE TRADE ENGINE")

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

            # -----------------------------
            # STATE ENGINE
            # -----------------------------
            state = st.session_state.active_trades.get(ticker, "WATCHING")

            msg = (
                f"{ticker} | ${price}\n"
                f"STATE: {state}\n"
                f"ENTRY {entry_low}-{entry_high}\n"
                f"STOP {stop} | T1 {t1} | T2 {t2}\n"
                f"RR {rr} | Setup {setup}% | Squeeze {squeeze}%"
            )

            last_time = st.session_state.last_alert.get(ticker, 0)

            # -----------------------------
            # ENTRY LOGIC
            # -----------------------------
            if state == "WATCHING":

                if entry_low <= price <= entry_high:

                    if now - last_time > cooldown:

                        st.session_state.active_trades[ticker] = "IN_TRADE"

                        alert_msg = "🔥 ENTRY FILLED: " + msg

                        st.success(alert_msg)
                        send_alert(alert_msg)

                        st.session_state.last_alert[ticker] = now

            # -----------------------------
            # ACTIVE TRADE MANAGEMENT
            # -----------------------------
            elif state == "IN_TRADE":

                # STOP LOSS
                if price <= stop:

                    if now - last_time > cooldown:

                        st.session_state.active_trades[ticker] = "STOPPED"

                        alert_msg = "🛑 STOP LOSS HIT: " + msg

                        st.error(alert_msg)
                        send_alert(alert_msg)

                        st.session_state.last_alert[ticker] = now

                # TARGET 1
                elif price >= t1 and price < t2:

                    if now - last_time > cooldown:

                        st.session_state.active_trades[ticker] = "TARGET_1"

                        alert_msg = "🎯 TARGET 1 HIT: " + msg

                        st.warning(alert_msg)
                        send_alert(alert_msg)

                        st.session_state.last_alert[ticker] = now

                # TARGET 2
                elif price >= t2:

                    if now - last_time > cooldown:

                        st.session_state.active_trades[ticker] = "TARGET_2"

                        alert_msg = "🚀 TARGET 2 HIT (FULL WIN): " + msg

                        st.success(alert_msg)
                        send_alert(alert_msg)

                        st.session_state.last_alert[ticker] = now

            # -----------------------------
            # DISPLAY LOGIC
            # -----------------------------
            if state == "WATCHING":
                st.info(msg)
            elif state == "IN_TRADE":
                st.warning(msg)
            elif state == "TARGET_2":
                st.success(msg)
            elif state == "STOPPED":
                st.error(msg)
            else:
                st.info(msg)

        # -----------------------------
        # TOP 10
        # -----------------------------
        st.subheader("🏆 Top 10 Opportunities")

        for r in results[:10]:
            trade = r.get("trade") or {}
            st.write(
                f"{r['ticker']} | ${r['price']} | "
                f"RR {trade.get('rr', 0)} | "
                f"STATE {st.session_state.active_trades.get(r['ticker'], 'WATCHING')}"
            )
