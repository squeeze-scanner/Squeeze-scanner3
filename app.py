import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

st.title("🚀 Squeeze Radar V16 (Stable Engine)")

tickers_input = st.text_input(
    "Enter tickers",
    "GME,AMC,TSLA,NVDA,BB,PLTR"
)

refresh_rate = st.slider("Refresh (sec)", 5, 60, 10)
start = st.toggle("Start")

# -----------------------------
# STATE
# -----------------------------
if "cache" not in st.session_state:
    st.session_state.cache = []

if "last_signal" not in st.session_state:
    st.session_state.last_signal = {}

if "last_alert" not in st.session_state:
    st.session_state.last_alert = {}

placeholder = st.empty()

# -----------------------------
# LOOP
# -----------------------------
if start:

    now = time.time()

    if now - st.session_state.get("last_run", 0) >= refresh_rate:

        tickers = [t.strip().upper() for t in tickers_input.split(",")]

        results = []

        for t in tickers:
            res = check_signal(t)
            if res:
                results.append(res)

        results.sort(key=lambda x: x["score"], reverse=True)

        st.session_state.cache = results
        st.session_state.last_run = now

    results = st.session_state.cache

    with placeholder.container():

        st.subheader("📊 Radar")

        if results:

            st.dataframe(results)

            st.subheader("🚨 Alerts")

            for r in results:

                ticker = r["ticker"]
                signal = r["signal"]
                score = r["score"]

                msg = f"{ticker} | {signal} | {score}"

                last = st.session_state.last_signal.get(ticker)

                if signal == "HIGH" and last != "HIGH":
                    st.error("🔥 " + msg)
                    send_alert("🔥 " + msg)

                elif signal == "MED":
                    st.warning("⚠️ " + msg)

                st.session_state.last_signal[ticker] = signal

            st.subheader("Top 5")

            for r in results[:5]:
                st.write(f"{r['ticker']} → {r['signal']} | ${r['price']} | Score {r['score']}")

        else:
            st.warning("No data")

    time.sleep(1)
    st.rerun()
