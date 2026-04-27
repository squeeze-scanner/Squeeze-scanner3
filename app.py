import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

st.title("🚀 V23 Squeeze Radar (Fixed Engine)")

user_tickers = st.text_input(
    "➕ Add extra tickers (comma separated)",
    "GME,AMC,TSLA"
)

refresh_rate = st.slider("Refresh interval (seconds)", 5, 60, 15)
start = st.toggle("🟢 Start Scanner")


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


if start:

    now = time.time()

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

        # sort by squeeze strength (REAL metric)
        results.sort(key=lambda x: x.get("squeeze_score", 0), reverse=True)

        st.session_state.cache = results
        st.session_state.last_run = now

    results = st.session_state.cache

    with placeholder.container():

        st.subheader("📊 Market Radar")
        st.write(f"Active tickers: {len(results)}")

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

                msg = (
                    f"{ticker} | {signal} | ${price}\n"
                    f"Bull {bull}% | Bear {bear}% | Squeeze {squeeze}%"
                )

                last_time = st.session_state.last_alert.get(ticker, 0)

                # FIXED ALERT LOGIC
                is_alert = (
                    squeeze >= 50 or
                    bull >= 70 or
                    bear >= 70
                )

                if is_alert:

                    if ticker not in st.session_state.alerted and now - last_time > cooldown:

                        st.error("🔥 " + msg)
                        send_alert("🔥 " + msg)

                        st.session_state.alerted.add(ticker)
                        st.session_state.last_alert[ticker] = now

                elif signal == "BULLISH":
                    st.success(msg)

                elif signal == "BEARISH":
                    st.warning(msg)

                else:
                    st.info(msg)

            st.subheader("🏆 Top 10")

            for r in results[:10]:
                st.write(
                    f"{r.get('ticker')} | {r.get('signal')} | "
                    f"${r.get('price')} | Squeeze {r.get('squeeze_score')}%"
                )
        else:
            st.info("Scanning...")

    # IMPORTANT FIX: removed st.rerun()
