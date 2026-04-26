import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

st.title("🚀 Squeeze Radar — V15 (Stable Engine)")

tickers_input = st.text_input(
    "Enter tickers (comma separated)",
    "GME,AMC,TSLA,NVDA,BB,PLTR"
)

refresh_rate = st.slider("Refresh interval (seconds)", 5, 60, 10)
start = st.toggle("🟢 Start Live Radar")

# -----------------------------
# STATE
# -----------------------------
if "results_cache" not in st.session_state:
    st.session_state.results_cache = []

if "last_alert_time" not in st.session_state:
    st.session_state.last_alert_time = {}

if "last_signal_state" not in st.session_state:
    st.session_state.last_signal_state = {}

if "last_run" not in st.session_state:
    st.session_state.last_run = 0

cooldown = 600
placeholder = st.empty()

# -----------------------------
# SAFE NORMALIZER (PREVENTS CRASHES)
# -----------------------------
def safe_row(r):
    return {
        "ticker": r.get("ticker", "N/A"),
        "signal": r.get("signal", "LOW"),
        "score": r.get("score", 0),
        "price": r.get("price", "N/A"),
        "RSI": r.get("RSI", "N/A"),
        "volume_intensity": r.get("volume_intensity", "N/A"),
    }

# -----------------------------
# RUN CONTROL
# -----------------------------
if start:

    now = time.time()

    # throttle scans
    if now - st.session_state.last_run >= refresh_rate:

        tickers = [t.strip().upper() for t in tickers_input.split(",")]

        new_results = []

        for t in tickers:
            try:
                res = check_signal(t)
                if res:
                    new_results.append(res)
            except Exception as e:
                st.write(f"Error on {t}: {e}")

        # normalize BEFORE storing
        new_results = [safe_row(r) for r in new_results]

        # sort safely
        new_results = sorted(new_results, key=lambda x: x.get("score", 0), reverse=True)

        st.session_state.results_cache = new_results
        st.session_state.last_run = now

    results = st.session_state.results_cache

    # -----------------------------
    # UI
    # -----------------------------
    with placeholder.container():

        st.subheader("📊 Live Radar (Stable Mode)")

        if results:

            st.dataframe(results)

            st.subheader("🚨 Alerts")

            for r in results:

                ticker = r.get("ticker", "N/A")
                signal = r.get("signal", "LOW")
                score = r.get("score", 0)
                price = r.get("price", "N/A")

                msg = (
                    f"{signal} SQUEEZE\n"
                    f"{ticker}\n"
                    f"Price: {price}\n"
                    f"Score: {score}"
                )

                last_time = st.session_state.last_alert_time.get(ticker, 0)
                last_state = st.session_state.last_signal_state.get(ticker)

                # HIGH ALERT
                if signal == "HIGH":
                    if last_state != "HIGH" and (now - last_time > cooldown):

                        st.error("🔥 " + msg)
                        send_alert("🔥 " + msg)

                        st.session_state.last_alert_time[ticker] = now
                        st.session_state.last_signal_state[ticker] = "HIGH"

                elif signal == "MED":
                    st.warning("⚠️ " + msg)
                    st.session_state.last_signal_state[ticker] = "MED"

                else:
                    st.info(msg)
                    st.session_state.last_signal_state[ticker] = "LOW"

            st.subheader("🏆 Top 5")

            for r in results[:5]:
                st.write(
                    f"{r.get('ticker', 'N/A')} → {r.get('signal', 'LOW')} | "
                    f"Price ${r.get('price', 'N/A')} | "
                    f"Score {r.get('score', 0)} | "
                    f"RSI {r.get('RSI', 'N/A')} | "
                    f"Vol {r.get('volume_intensity', 'N/A')}"
                )

        else:
            st.warning("No signals detected yet")

    # refresh cycle
    time.sleep(1)
    st.rerun()
