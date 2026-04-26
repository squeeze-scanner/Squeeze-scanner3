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
        print(e)

# 🔥 SORT BY SCORE (THIS IS KEY)
results = sorted(results, key=lambda x: x["squeeze_score"], reverse=True)

if results:
    st.success("Squeeze Rankings")
    st.dataframe(results)
else:
    st.warning("No data returned")
