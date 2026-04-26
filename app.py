import streamlit as st
from scanner import check_signal

st.title("🚀 Short Squeeze Scanner")

st.write("Enter tickers separated by commas")

tickers = st.text_input("Tickers", "GME,AMC,TSLA")

if st.button("Scan"):
    tickers = [t.strip().upper() for t in tickers.split(",")]

    results = []

    for t in tickers:
        try:
            res = check_signal(t)
            if res:
                results.append(res)
        except:
            pass

    if results:
        st.success("Potential Squeeze Candidates Found")
        st.dataframe(results)
    else:
        st.warning("No signals found")
