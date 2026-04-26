import streamlit as st
import time
from scanner import check_signal

st.title("🚀 Squeeze Radar v7")

tickers_input = st.text_input(
    "Enter tickers (comma separated)",
    "GME,AMC,TSLA,NVDA,BB,PLTR"
)

auto_refresh = st.checkbox("🔄 Auto-refresh (5 seconds)")

run = st.button("Run Radar")

if run:

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
    # SORT BY SCORE
    # -----------------------------
    results = sorted(results, key=lambda x: x.get("squeeze_score", 0), reverse=True)

    st.subheader("📊 Squeeze Rankings")

    if results:
        st.dataframe(results)

        # -----------------------------
        # ALERTS
        # -----------------------------
        st.subheader("🚨 Alerts")

        for r in results:
            score = r.get("squeeze_score", 0)
            ticker = r.get("ticker", "N/A")

            if score >= 6:
                st.error(f"🔥 HIGH SQUEEZE ALERT: {ticker} ({score})")
            elif score >= 4:
                st.warning(f"⚠️ Watch: {ticker} ({score})")

        # -----------------------------
        # TOP WATCHLIST
        # -----------------------------
        st.subheader("🏆 Top Squeeze Watchlist")

        for r in results[:5]:
            st.write(
                f"{r.get('ticker')} → Score {r.get('squeeze_score')} | "
                f"RSI {r.get('RSI')} | Vol {r.get('volume_spike')}"
            )

        # -----------------------------
        # SENTIMENT LABELS
        # -----------------------------
        st.subheader("📊 Market Sentiment")

        def label(score):
            if score >= 6:
                return "🔥 STRONG SQUEEZE SETUP"
            elif score >= 4:
                return "⚠️ WATCH"
            else:
                return "LOW"

        for r in
