import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

st.title("🚀 Squeeze Radar — V8 LIVE MODE (Event Engine)")

tickers_input = st.text_input(
    "Enter tickers (comma separated)",
    "GME,AMC,TSLA,NVDA,BB,PLTR"
)

refresh_rate = st.slider("Refresh interval (seconds)", 5, 60, 15)

start = st.checkbox("🟢 Start Live Radar")

placeholder = st.empty()

if start:

    tickers = [t.strip().upper() for t in tickers_input.split(",")]

    seen_alerts = set()  # 🔥 prevents duplicate Telegram spam

    while True:

        results = []

        # -----------------------------
        # SCAN LOOP
        # -----------------------------
        for t in tickers:
            try:
                res = check_signal(t)
                if res:
                    results.append(res)
            except Exception as e:
                st.write(f"Error on {t}: {e}")

        # -----------------------------
        # SORT (HIGH first)
        # -----------------------------
        order = {"HIGH": 3, "MED": 2, "LOW": 1, "NONE": 0}
        results = sorted(results, key=lambda x: order.get(x.get("signal", "NONE")), reverse=True)

        with placeholder.container():

            st.subheader("📊 Live Squeeze Events (V8)")

            if results:
                st.dataframe(results)

                st.subheader("🚨 Live Event Alerts")

                for r in results:

                    ticker = r.get("ticker")
                    signal = r.get("signal")
                    events = r.get("events", [])

                    msg = f"{signal} SQUEEZE SIGNAL\n{ticker}\nEvents: {', '.join(events)}"

                    # -----------------------------
                    # HIGH SIGNAL = TELEGRAM ALERT
                    # -----------------------------
                    if signal == "HIGH" and ticker not in seen_alerts:

                        st.error("🔥 " + msg)
                        send_alert("🔥 " + msg)

                        seen_alerts.add(ticker)

                    elif signal == "MED":
                        st.warning("⚠️ " + msg)

                    elif signal == "LOW":
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

        time.sleep(refresh_rate)
        st.rerun()
