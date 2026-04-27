import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

st.title("🚀 V2 Squeeze Radar (Execution Engine)")

# -----------------------------
# INPUTS
# -----------------------------
user_tickers = st.text_input(
    "➕ Add extra tickers (comma separated)",
    "GME,AMC,TSLA"
)

refresh_rate = st.slider("Refresh interval (seconds)", 5, 60, 15)
start = st.toggle("🟢 Start Scanner")

# -----------------------------
# UNIVERSE
# -----------------------------
def get_full_universe():
    base = [
        "AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA","JPM",
        "V","XOM","PG","MA","HD","CVX","PEP","KO","WMT","BAC"
    ]

    momentum = [
        "PLTR","GME","AMC","BB","NIO","SOFI","RIVN","LCID",
        "AMD","INTC","PYPL","UBER","SQ","SHOP","BABA"
    ]

    return list(set(base + momentum))


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

if "alerted" not in st.session_state:
    st.session_state.alerted = set()

cooldown = 600
placeholder = st.empty()

# -----------------------------
# MAIN LOOP
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

        # SORT BY TRUE EXECUTION VALUE
        results.sort(key=lambda x: x.get("score", 0), reverse=True)

        st.session_state.cache = results
        st.session_state.last_run = now

    results = st.session_state.cache

    # -----------------------------
    # UI
    # -----------------------------
    with placeholder.container():

        st.subheader("📊 Market Radar")
        st.write(f"Active tickers: {len(results)}")

        if results:

            st.dataframe(results)

            st.subheader("🚀 V2 TRADE EXECUTION SIGNALS")

            for r in results:

                ticker = r.get("ticker")
                signal = r.get("signal", "NEUTRAL")
                price = r.get("price", 0)

                squeeze = r.get("squeeze_score", 0)
                setup = r.get("setup_score", 0)
                alerts = r.get("alerts", [])

                trade = r.get("trade_plan") or {}
                state = trade.get("state", "WAITING")
                rr = trade.get("rr", 0)

                msg = (
                    f"{ticker} | {signal} | ${price}\n"
                    f"STATE: {state}\n"
                    f"Setup {setup}% | Squeeze {squeeze}% | RR {rr}"
                )

                last_time = st.session_state.last_alert.get(ticker, 0)

                # -----------------------------
                # V2 EXECUTION LOGIC (IMPORTANT)
                # -----------------------------
                is_breakout = state == "BREAKOUT"
                is_entry = state == "AT_ENTRY"

                is_high_quality = setup >= 65 and squeeze >= 55
                is_extreme = setup >= 80 and rr >= 1.5

                is_alert = (
                    is_extreme or
                    (is_high_quality and is_entry) or
                    (is_breakout and rr >= 1.3)
                )

                if is_alert:

                    if ticker not in st.session_state.alerted and now - last_time > cooldown:

                        if is_extreme:
                            alert_msg = "🔥 EXTREME EXECUTION SETUP: " + msg
                            st.error(alert_msg)
                        else:
                            alert_msg = "⚡ EXECUTION ALERT: " + msg
                            st.warning(alert_msg)

                        send_alert(alert_msg)

                        st.session_state.alerted.add(ticker)
                        st.session_state.last_alert[ticker] = now

                elif signal == "BULLISH":
                    st.success(msg)

                elif signal == "BEARISH":
                    st.warning(msg)

                else:
                    st.info(msg)

            # -----------------------------
            # TOP 10
            # -----------------------------
            st.subheader("🏆 Top 10 Execution Candidates")

            for r in results[:10]:

                trade = r.get("trade_plan") or {}

                st.write(
                    f"{r.get('ticker')} | {r.get('signal')} | "
                    f"${r.get('price')} | "
                    f"RR {trade.get('rr', 0)} | "
                    f"STATE {trade.get('state', 'WAITING')}"
                )

        else:
            st.info("Scanning market...")
