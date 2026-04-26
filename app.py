import streamlit as st
from scanner import check_signal

st.title("Short Squeeze Scanner")

tickers = st.text_input("Enter tickers", "GME,AMC,TSLA")
tickers = [t.strip().upper() for t in tickers.split(",")]

if st.button("Scan"):
    results = []

    for t in tickers:
        res = check_signal(t)
        if res:
            results.append(res)

    if results:
        st.write("Potential Squeeze Candidates")
        st.dataframe(results)
    else:
        st.write("No signals found")
