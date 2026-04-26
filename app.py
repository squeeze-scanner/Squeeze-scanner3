import streamlit as st
from scanner import check_signal

st.title("🚀 Squeeze Radar v2")

tickers_input = st.text_input("Enter tickers", "GME,AMC,TSLA,NVDA,BB")

if st.button("Scan Radar"):

    tickers = [t.strip().upper() for t in tickers_input.split(",")]

    results = []

    for t in tickers:
        try:
            res = check_signal(t)
            if res:
                results.append(res)
        except:
            pass

    # 🔥 SORT BY SQUEEZE SCORE (KEY FEATURE)
    results = sorted(results, key=lambda x: x["squeeze_score"], reverse=True)

    st.subheader("📊 Squeeze Candidates")

    if results:
        st.dataframe(results)
    else:
        st.warning("No data returned")
