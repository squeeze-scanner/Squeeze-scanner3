from telegram import send_alert
import streamlit as st
import time
from scanner import check_signal

st.title("🚀 Squeeze Radar v7")

tickers_input = st.text_input(
    "Enter tickers (comma separated)",
    "GME,AMC,TSLA,NVDA,BB,PLTR"
)

auto_refresh = st.checkbox("🔄 Auto-refresh (5 seconds)")

if st.button("Run Radar"):

    tickers = [t.strip().upper() for t in tickers_input.split(",")]

    results = []

    # -----------------------------
    # RUN SCAN
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

    st.subheader("📊 Squeeze Rankings")

    if results:
        st.dataframe(results)

        st.subheader("🚨 Alerts")

        for r in results:
            score = r.get("squeeze_score", 0)
            ticker = r.get("ticker", "N/A")

            if score >= 6:
                st.error(f"🔥 HIGH SQUEEZE ALERT: {ticker} ({score})")
            elif score >= 4:
                st.warning(f"⚠️ Watch: {ticker} ({score})")

        st.subheader("🏆 Top Watchlist")

        for r in results[:5]:
            st.write(
                f"{r.get('ticker')} → Score {r.get('squeeze_score')} | "
                f"RSI {r.get('RSI')} | Vol {r.get('volume_spike')}"
            )

    else:
        st.warning("No results returned. Try different tickers.")

# -----------------------------
# AUTO REFRESH
# -----------------------------
if auto_refresh:
    time.sleep(5)
    st.rerun()
