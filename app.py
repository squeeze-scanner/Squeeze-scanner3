import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

st.title("🚀 Squeeze Radar — V9 (Pro Live Engine)")

tickers_input = st.text_input(
    "Enter tickers (comma separated)",
    "GME,AMC,TSLA,NVDA,BB,PLTR"
)

refresh_rate = st.slider("Refresh interval (seconds)", 5, 60, 10)

start = st.toggle("🟢 Start Live Radar")

# -----------------------------
# SESSION STATE (PERSISTENT MEMORY)
# -----------------------------
if "last_alert_time" not in st.session_state:
    st.session_state.last_alert_time = {}

if "run_count" not in st.session_state:
    st.session_state.run_count = 0

cooldown = 600  # 10 minutes

placeholder = st.empty()

# -----------------------------
# AUTO RUN LOOP (SAFE STREAMLIT STYLE)
# -----------------------------
if start:

    tickers = [t.strip().upper() for t in tickers_input.split(",")]

    # Increment run counter
    st.session_state.run_count += 1

    results = []

    # -----------------------------
    # SCAN
    # -----------------------------
    for t in tickers:
        try:
            res = check_signal(t)
            if res:
                results.append(res)
        except Exception as e:
            st.write(f"Error on {t}: {e}")

    # -----------------------------
    # SORT BY SIGNAL STRENGTH
    # -----------------------------
    order = {"HIGH": 3, "MED": 2, "LOW": 1, "NONE": 0}
    results = sorted(results, key=lambda x: order.get(x.get("signal", "NONE")), reverse=True)

    with placeholder.container():

        st.subheader(f"📊 Live Radar (Run #{st.session_state.run_count})")

        if results:
            st.dataframe(results)

            st.subheader("🚨 Alerts")

            now = time.time()

            for r in results:

                ticker = r.get("ticker")
                signal = r.get("signal")
                events = r.get("events", [])

                last_time = st.session_state.last_alert_time.get(ticker, 0)

                msg = f"{signal} SQUEEZE SIGNAL\n{ticker}\nEvents: {', '.join(events)}"

                # -----------------------------
                # HIGH SIGNAL = TELEGRAM ALERT (COOLDOWN)
                # -----------------------------
                if signal == "HIGH":

                    if now - last_time > cooldown:

                        st.error("🔥 " + msg)
                        send_alert("🔥 " + msg)

                        st.session_state.last_alert_time[ticker] = now

                elif signal == "MED":
                    st.warning("⚠️ " + msg)

                else:
                    st.info(msg)

            st.subheader("🏆 Top 5 Signals")

            for r in results[:5]:
                st.write(
                    f"{r.get('ticker')} → {r.get('signal')} | "
                    f"Events: {', '.join(r.get('events', []))} | "
                    f"RSI {r.get('RSI')} | Vol {r.get('volume_spike')}"
                )

        else:
            st.warning("No signals detected")

    # -----------------------------
    # SAFE AUTO REFRESH (NO LOOP)
    # -----------------------------
    time.sleep(refresh_rate)
    st.rerun()
