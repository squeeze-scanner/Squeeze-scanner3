import streamlit as st
from scanner import check_signal

st.title("🚀 Short Squeeze Scanner")

st.write("Enter tickers separated by commas")

tickers_input = st.text_input("Tickers", "GME,AMC,TSLA")

if st.button("Scan"):
    tickers = [t.strip().upper() for t in tickers_input.split(",")]

    results = []

    for t in tickers:
        try:
            res = check_signal(t)
            if res:
                results.append(res)
        except Exception as e:
            print(f"Error on {t}: {e}")

    if results:
        st.success("Signals Found")
        st.dataframe(results)
    else:
        st.warning("No signals found (try more volatile tickers)")
