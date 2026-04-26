import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

st.title("🚀 Squeeze Radar — V14.2 (Stable Engine)")

tickers_input = st.text_input(
    "Enter tickers (comma separated)",
    "GME,AMC,TSLA,NVDA,BB,PLTR"
)

refresh_rate = st.slider("Refresh interval (seconds)", 5, 60, 10)

start = st.toggle("🟢 Start Live Radar")

# -----------------------------
# SESSION STATE
# -----------------------------
if "last_alert_time" not in st.session_state:
    st.session_state.last_alert_time = {}

if "last_signal_state" not in st.session_state:
    st.session_state.last_signal_state = {}

cooldown = 600

placeholder = st.empty()

# -----------------------------
# MAIN LOOP
# -----------------------------
if start:

    tickers = [t.strip().upper() for t in tickers_input.split(",")]

    results = []

    for t in tickers:
        try:
            res = check_signal(t)
            if res:
                results.append(res)
        except Exception as e:
            st.write(f"Error on {t}: {e}")

    results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)

    with placeholder.container():

        st.subheader("📊 Live Radar")

        if results:
            st.dataframe(results)

            st.subheader("🚨 Alerts")

            now = time.time()

            for r in results:

                ticker = r["ticker"]
                signal = r.get("signal", "LOW")
                score = r.get("score", 0)

                msg = f"{signal} SQUEEZE\n{ticker}\nPrice: {r.get('price')}\nScore: {score}"

                last_time = st.session_state.last_alert_time.get(ticker, 0)
                last_state = st.session_state.last_signal_state.get(ticker)

                # -----------------------------
                # ONLY ALERT ON STATE CHANGE
                # -----------------------------
                if signal == "HIGH":

                    if (
                        last_state != "HIGH"
                        and now - last_time > cooldown
                    ):
                        st.error("🔥 " + msg)
                        send_alert("🔥 " + msg)

                        st.session_state.last_alert_time[ticker] = now
                        st.session_state.last_signal_state[ticker] = "HIGH"

                elif signal == "MED":
                    st.warning("⚠️ " + msg)
                    st.session_state.last_signal_state[ticker] = "MED"

                else:
                    st.info(msg)
                    st
