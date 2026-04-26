import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

st.title("🚀 Squeeze Radar — V12")

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

if "seen_alerts" not in st.session_state:
    st.session_state.seen_alerts = set()

if "run_count" not in st.session_state:
    st.session_state.run_count = 0

cooldown = 600

placeholder = st.empty()

# -----------------------------
# RUN LOOP (SAFE STREAMLIT STYLE)
# -----------------------------
if start:

    tickers = [t.strip().upper() for t in tickers_input.split(",")]

    st.session_state.run_count += 1

    results = []

    for t in tickers:
        try:
            res = check_signal(t)
            if res:
                results.append(res)
        except Exception as e:
            st.write(f"Error on {t}: {e}")

    # sort by score
    results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)

    with placeholder.container():

        st.subheader(f"📊 Live Radar (Run #{st.session_state.run_count})")

        if results:
            st.dataframe(results)

            st.subheader("🚨 Alerts")

            now = time.time()

            for r in results:

                ticker = r["ticker"]
                signal = r.get("signal", "LOW")
                score = r.get("score", 0)

                last_time = st.session_state.last_alert_time.get(ticker, 0)

                msg = f"{signal} SQUEEZE\n{ticker}\nPrice: {r.get('price')}\nScore: {score}"

                # HIGH ALERT ONLY ONCE PER COOLDOWN
                if signal == "HIGH":

                    if now - last_time > cooldown and ticker not in st.session_state.seen_alerts:

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
                    f"{r['ticker']} → {r['signal']} | "
                    f"Price ${r.get('price')} | "
                    f"Score {r.get('score')} | "
                    f"RSI {r.get('RSI')} | "
                    f"Vol {r.get('volume_intensity')}"
                )

        else:
            st.warning("No signals detected")

    time.sleep(refresh_rate)
    st.rerun()
