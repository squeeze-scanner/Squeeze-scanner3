import streamlit as st
import time
from scanner import check_signal
from telegram import send_alert

st.title("🚀 Squeeze Radar — LIVE MODE")

tickers_input = st.text_input(
    "Enter tickers (comma separated)",
    "GME,AMC,TSLA,NVDA,BB,PLTR"
)

refresh_rate = st.slider("Refresh interval (seconds)", 5, 60, 15)

start = st.checkbox("🟢 Start Live Radar")

placeholder = st.empty()

if start:

    tickers = [t.strip().upper() for t in tickers_input.split(",")]

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
        # SORT RESULTS
        # -----------------------------
        results = sorted(results, key=lambda x: x.get("squeeze_score", 0), reverse=True)

        with placeholder.container():

            st.subheader("📊 Live Squeeze Rankings")

            if results:
                st.dataframe(results)

                st.subheader("🚨 Live Alerts")

                for r in results:
                    score = r.get("squeeze_score", 0)
                    ticker = r.get("ticker", "N/A")

                    if score >= 6:
                        msg = f"🔥 LIVE HIGH SQUEEZE\n{ticker}\nScore: {score}"
                        st.error(msg)
                        send_alert(msg)

                    elif score >= 4:
                        msg = f"⚠️ LIVE WATCH\n{ticker}\nScore: {score}"
                        st.warning(msg)

                st.subheader("🏆 Top 5 Live")

                for r in results[:5]:
                    st.write(
                        f"{r.get('ticker')} → Score {r.get('squeeze_score')} | "
                        f"RSI {r.get('RSI')} | Vol {r.get('volume_spike')}"
                    )

            else:
                st.warning("No data available")

        time.sleep(refresh_rate)
        st.rerun()
