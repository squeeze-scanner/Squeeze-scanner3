import streamlit as st
from scanner import check_signal

st.title("🚀 Squeeze Radar v5/v6")

tickers_input = st.text_input(
    "Enter tickers (comma separated)",
    "GME,AMC,TSLA,NVDA,BB,PLTR"
)

if st.button("Run Radar"):

    tickers = [t.strip().upper() for t in tickers_input.split(",")]

    results = []

    # -----------------------------
    # BUILD RESULTS LIST
    # -----------------------------
    for t in tickers:
        try:
            res = check_signal(t)
            if res is not None:
                results.append(res)
        except Exception as e:
            st.write(f"Error on {t}: {e}")

    # -----------------------------
    # SORT RESULTS BY SCORE
    # -----------------------------
    results = sorted(results, key=lambda x: x.get("squeeze_score", 0), reverse=True)

    st.subheader("📊 Squeeze Rankings")

    if results:

        st.dataframe(results)

        st.subheader("🚨 Alerts")

        # -----------------------------
        # SAFE ALERT LOOP (NO ERRORS)
        # -----------------------------
        for r in results:

            alert = r.get("alert", "LOW")

            if alert == "HIGH":
                st.error(f"🔥 HIGH SQUEEZE ALERT: {r.get('ticker')} ({r.get('squeeze_score')})")

            elif alert == "MED":
                st.warning(f"⚠️ Watch: {r.get('ticker')} ({r.get('squeeze_score')})")

    else:
        st.warning("No results returned. Try different tickers.")
