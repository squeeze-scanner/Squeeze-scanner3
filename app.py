import streamlit as st
import time
from engine_v19 import AutonomousScanner
from telegram import send_alert

st.title("🚀 V19 Autonomous Squeeze Scanner")

# -----------------------------
# STATE
# -----------------------------
if "engine" not in st.session_state:
    st.session_state.engine = AutonomousScanner()
    st.session_state.engine.start(interval=10)

if "last_signal" not in st.session_state:
    st.session_state.last_signal = {}

placeholder = st.empty()

engine = st.session_state.engine

# -----------------------------
# UI LOOP
# -----------------------------
while True:

    results = engine.get()

    with placeholder.container():

        st.subheader("📊 Autonomous Market Radar")

        if results:

            st.dataframe(results)

            st.subheader("🚨 Live Signals")

            for r in results:

                ticker = r["ticker"]
                signal = r["signal"]
                score = r["score"]

                msg = f"{ticker} | {signal} | {score}"

                last = st.session_state.last_signal.get(ticker)

                # alert only on change
                if signal == "HIGH" and last != "HIGH":
                    st.error("🔥 " + msg)
                    send_alert("🔥 " + msg)

                elif signal == "MED":
                    st.warning("⚠️ " + msg)

                st.session_state.last_signal[ticker] = signal

            st.subheader("Top 5 Movers")

            for r in results[:5]:
                st.write(
                    f"{r['ticker']} → {r['signal']} | "
                    f"${r['price']} | Score {r['score']}"
                )

        else:
            st.info("Scanning market automatically...")

    time.sleep(5)
    st.rerun()
