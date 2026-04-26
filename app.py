import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

st.title("🚀 Squeeze Radar — V12 (Intelligence Engine)")

tickers_input = st.text_input(
    "Enter tickers (comma separated)",
    "GME,AMC,TSLA,NVDA,BB,PLTR"
)

refresh_rate = st.slider("Refresh interval (seconds)", 5, 60, 10)

start = st.toggle("🟢 Start Live Radar")

# -----------------------------
# SESSION STATE (MEMORY SYSTEM)
# -----------------------------
if "last_alert_time" not in st.session_state:
    st.session_state.last_alert_time = {}

if "run_count" not in st.session_state:
    st.session_state.run_count = 0

if "seen_alerts" not in st.session_state:
    st.session_state.seen_alerts = set()

cooldown = 600  # 10 minutes

placeholder = st.empty()

# -----------------------------
# MAIN LOOP (SAFE STRUCTURE)
# -----------------------------
if start:

    tickers = [t.strip().upper() for t in tickers_input.split(",")]

    st.session_state.run_count += 1

    results = []

    # -----------------------------
    # SCAN ENGINE
    # -----------------------------
    for t in tickers:
        try:
            res = check_signal(t)
            if res:
                results.append(res)
        except Exception as e:
            st.write(f"Error on {t}: {e}")

    # -----------------------------
    # SORT BY SCORE OR SIGNAL
    # -----------------------------
    def score_key(x):
        return x.get("score", 0) if "score" in x else 0

    results = sorted(results, key=score_key, reverse=True)

    with placeholder.container():

        st.subheader(f"📊 V12 Live Radar (Run #{st.session_state.run_count})")

        if results:
            st.dataframe(results)

            st.subheader("🚨 Alerts")

            now = time.time()

            for r in results:

                ticker = r.get("ticker")
                signal = r.get("signal", "LOW")
                score = r.get("score", 0)

                last_time = st.session_state.last_alert_time.get(ticker, 0)

                msg = f"{signal} SQUEEZE\n{ticker}\nScore: {score}"

                # -----------------------------
                # HIGH SIGNAL ALERT (NO DUPLICATES)
                # -----------------------------
                if signal == "HIGH":

                    if (now - last_time > cooldown) and (ticker not in st.session_state.seen_alerts):

                        st.error("🔥 " + msg)
                        send_alert("🔥 " + msg)

                        st.session_state.last_alert_time[ticker] = now
                        st.session_state.seen_alerts.add(ticker)

                elif signal == "MED":
                    st.warning("⚠️ " + msg)

                else:
                    st.info(msg)

            st.subheader("🏆 Top 5 Signals")

            for r in results[:5]:
                st.write(
                    f"{r.get('ticker')} → {r.get('signal')} | "
                    f"Score {r.get('score', 0)} | "
                    f"RSI {r.get('RSI')} | "
                    f"Vol {r.get('volume_intensity', 'N/A')}"
                )

        else:
            st.warning("No signals detected")

    # -----------------------------
    # SAFE REFRESH (NO WHILE LOOP)
    # -----------------------------
    time.sleep(refresh_rate)
    st.rerun()
