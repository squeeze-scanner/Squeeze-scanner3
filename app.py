import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

st.title("🚀 Squeeze Radar V17 (Engine Core)")

tickers_input = st.text_input(
    "Tickers",
    "GME,AMC,TSLA,NVDA,BB,PLTR"
)

refresh_rate = st.slider("Scan Interval (sec)", 5, 60, 10)
start = st.toggle("Start Engine")

# -----------------------------
# STATE
# -----------------------------
if "cache" not in st.session_state:
    st.session_state.cache = []

if "last_signal" not in st.session_state:
    st.session_state.last_signal = {}

if "last_alert" not in st.session_state:
    st.session_state.last_alert = {}

if "last_scan" not in st.session_state:
    st.session_state.last_scan = 0

placeholder = st.empty()

# -----------------------------
# ENGINE LOOP (CONTROLLED)
# -----------------------------
if start:

    now = time.time()

    tickers = [t.strip().upper() for t in tickers_input.split(",")]

    # -----------------------------
    # SCAN ONLY WHEN DUE
    # -----------------------------
    if now - st.session_state.last_scan >= refresh_rate:

        results = []

        for t in tickers:
            res = check_signal(t)
            if res:
                results.append(res)

        results.sort(key=lambda x: x["score"], reverse=True)

        st.session_state.cache = results
        st.session_state.last_scan = now

    results = st.session_state.cache

    # -----------------------------
    # RENDER
    # -----------------------------
    with placeholder.container():

        st.subheader("📊 Live Radar V17")

        if results:

            st.dataframe(results)

            st.subheader("🚨 Alerts")

            for r in results:

                ticker = r["ticker"]
                signal = r["signal"]
                score = r["score"]

                msg = f"{ticker} | {signal} | {score}"

                last = st.session_state.last_signal.get(ticker)

                # ONLY ON CHANGE
                if signal == "HIGH" and last != "HIGH":
                    st.error("🔥 " + msg)
                    send_alert("🔥 " + msg)

                elif signal == "MED":
                    st.warning("⚠️ " + msg)

                st.session_state.last_signal[ticker] = signal

            st.subheader("Top 5")

            for r in results[:5]:
                st.write(
                    f"{r['ticker']} → {r['signal']} | "
                    f"${r['price']} | Score {r['score']} | "
                    f"RSI {r['RSI']} | Vol {r['volume']}"
                )

        else:
            st.warning("No data")

    time.sleep(1)
    st.rerun()
