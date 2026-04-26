import streamlit as st
from scanner import check_signal

st.title("🚀 Squeeze Radar v4")

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

    # 🔥 SORT BY SCORE
    results = sorted(results, key=lambda x: x["squeeze_score"], reverse=True)

    st.subheader("📊 Ranked Squeeze Candidates")

    if results:
        st.dataframe(results)
    else:
        st.warning("No data returned")
