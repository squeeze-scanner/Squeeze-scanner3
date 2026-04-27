import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

# -----------------------------
# TITLE
# -----------------------------
st.title("🚀 V27 Squeeze Radar (Predictive Engine)")


# -----------------------------
# INPUT
# -----------------------------
user_tickers = st.text_input(
    "➕ Add extra tickers (comma separated)",
    "GME,AMC,TSLA"
)

refresh_rate = st.slider("Refresh interval (seconds)", 5, 60, 10)
scan_size = st.slider("📊 Max tickers to scan", 10, 150, 50)
start = st.toggle("🟢 Start Scanner")


# -----------------------------
# UNIVERSE (CACHED)
# -----------------------------
@st.cache_data(ttl=300)
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


# -----------------------------
# MAIN ENGINE
# -----------------------------
if start:

    now = time.time()

    if now - st.session_state.last_run >= refresh_rate:

        universe = merge_universe(user_tickers)[:scan_size]

        results = []

        for t in universe:
            try:
                res = check_signal(t)
                if res:
                    results.append(res)
            except:
                continue

        results.sort(key=lambda x: x.get("confidence", 0), reverse=True)

        st.session_state.cache = results
        st.session_state.last_run = now

    results = st.session_state.cache


    # -----------------------------
    # UI
    # -----------------------------
    st.subheader("📊 Market Radar")

    st.write(f"Scanning: {scan_size} tickers")

    if results:

        st.dataframe(results)

        st.subheader("🚨 Alerts")

        for r in results:

            ticker = r.get("ticker")
            signal = r.get("signal")
            price = r.get("price")

            squeeze = r.get("squeeze_score", 0)
            bull = r.get("bull_prob", 0)
            bear = r.get("bear_prob", 0)

            alert_tags = r.get("alerts", [])

            # -----------------------------
            # BUILD MESSAGE (FIXED)
            # -----------------------------
            msg = (
                f"{ticker} | {signal} | ${price}\n"
                f"Bull {bull}% | Bear {bear}%\n"
                f"Squeeze {squeeze}%\n"
                f"Alerts: {', '.join(alert_tags) if alert_tags else 'None'}"
            )

            last_time = st.session_state.last_alert.get(ticker, 0)

            # -----------------------------
            # ALERT TRIGGER LOGIC (FIXED)
            # -----------------------------
            should_alert = (
                "HIGH_BULL_CONFIDENCE" in alert_tags or
                "HIGH_BEAR_CONFIDENCE" in alert_tags or
                "HIGH_SQUEEZE_POTENTIAL" in alert_tags
            )

            if should_alert:

                if ticker not in st.session_state.alerted and now - last_time > cooldown:

                    st.error("🔥 " + msg)

                    success = send_alert("🔥 " + msg)

                    # only mark if Telegram succeeds
                    if success:
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
        st.subheader("🏆 Top 10 Candidates")

        for r in results[:10]:
            st.write(
                f"{r.get('ticker')} → {r.get('signal')} | "
                f"${r.get('price')} | "
                f"Bull {r.get('bull_prob')}% | "
                f"Bear {r.get('bear_prob')}% | "
                f"Squeeze {r.get('squeeze_score')}%"
            )

    else:
        st.warning("No signals detected yet")
