import streamlit as st
from scanner import check_signal

st.title("🚀 Squeeze Radar v5")

tickers_input = st.text_input(
    "Enter tickers",
    "GME,AMC,TSLA,NVDA,BB,PLTR"
)

if st.button("Run Radar"):

    tickers = [t.strip().upper() for t in tickers_input.split(",")]

    results = []

    for t in tickers:
        try:
            res = check_signal(t)
            if res:
                results.append(res)
        except:
            pass

    # sort by squeeze pressure
    results = sorted(results, key=lambda x: x["squeeze_score"], reverse=True)

    st.subheader("📊 Squeeze Pressure Rankings")

    if results:
        st.dataframe(results)

        st.subheader("🚨 Alerts")

        for r in results:
            if r["alert"] == "HIGH":
                st.error(f"🔥 HIGH SQUEEZE ALERT: {r['ticker']} ({r['squeeze_score']})")
            elif r["alert"] == "MED":
                st.warning(f"⚠️ Watch: {r['ticker']} ({r['squeeze_score']})")
    else:
        st.warning("No data returned")
