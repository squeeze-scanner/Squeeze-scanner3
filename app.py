import streamlit as st
from scanner import check_signal

st.title("🚀 Short Squeeze Scanner")

tickers_input = st.text_input("Enter tickers (comma separated)", "GME,AMC,TSLA")

if st.button("Scan"):

    tickers = [t.strip().upper() for t in tickers_input.split(",")]

    results = []

    for t in tickers:
        try:
            res = check_signal(t)
            if res:
                results.append(res)
        except Exception as e:
            st.write(f"Error on {t}: {e}")

    # sort by score (important)
    results = sorted(results, key=lambda x: x["squeeze_score"], reverse=True)

    st.subheader("Results")

    st.dataframe(results)
