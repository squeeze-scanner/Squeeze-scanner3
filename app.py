import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

# -----------------------------
# TITLE
# -----------------------------
st.title("🚀 V23 Squeeze Radar (Full Market + Short Data)")

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
# UNIVERSE
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

if "alerted" not in st.session_state:
    st.session_state.alerted = set()

placeholder = st.empty()
cooldown = 600

# -----------------------------
# MAIN ENGINE
# -----------------------------
if start:

    now = time.time()

    # throttle scans
    if now - st.session_state.last_run >= refresh_rate:

        tickers = merge_universe(user_tickers)

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

        st.write(f"Scanning {len(merge_universe(user_tickers))} tickers")

        if results:

            # FULL TABLE
            st.dataframe(results)

            st.subheader("🚨 Alerts")

            for r in results:

                ticker = r.get("ticker", "N/A")
                signal = r.get("signal", "LOW")
                score = r.get("score", 0)
                price = r.get("price", "N/A")

                msg = (
                    f"{ticker} | {signal} | Score {score} | ${price} | "
                    f"Short {r.get('short_%')}% | DTC {r.get('days_to_cover')}"
                )

                last_time = st.session_state.last_alert.get(ticker, 0)

                # -----------------------------
                # ALERT LOGIC (NO SPAM)
                # -----------------------------
                if signal == "HIGH":

                    if (
                        ticker not in st.session_state.alerted
                        and now - last_time > cooldown
                    ):
                        st.error("🔥 " + msg)
                        send_alert("🔥 " + msg)

                        st.session_state.alerted.add(ticker)
                        st.session_state.last_alert[ticker] = now

                elif signal == "MED":
                    st.warning("⚠️ " + msg)

                else:
                    st.info(msg)

            # -----------------------------
            # TOP 10
            # -----------------------------
            st.subheader("🏆 Top 10 Squeeze Candidates")

            for r in results[:10]:
                st.write(
                    f"{r.get('ticker')} → {r.get('signal')} | "
                    f"${r.get('price')} | Score {r.get('score')} | "
                    f"Short {r.get('short_%')}% | "
                    f"DTC {r.get('days_to_cover')}"
                )

        else:
            st.info("Scanning market...")

    # light refresh loop
    time.sleep(1)
    st.rerun()
