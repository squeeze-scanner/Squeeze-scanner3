import streamlit as st
from engine import RadarEngine
from telegram import send_alert

st.title("🚀 Squeeze Radar V18 — Institutional Engine")

tickers_input = st.text_input(
    "Tickers",
    "GME,AMC,TSLA,NVDA,BB,PLTR"
)

refresh_rate = st.slider("Engine Refresh (sec)", 2, 30, 5)
start = st.toggle("Start Institutional Engine")

# -----------------------------
# STATE
# -----------------------------
if "engine" not in st.session_state:
    st.session_state.engine = None

if "last_signal" not in st.session_state:
    st.session_state.last_signal = {}

placeholder = st.empty()

# -----------------------------
# START ENGINE ONCE
# -----------------------------
if start:

    tickers = [t.strip().upper() for t in tickers_input.split(",")]

    if st.session_state.engine is None:
        engine = RadarEngine(tickers)
        engine.start(refresh_rate)
        st.session_state.engine = engine

    engine = st.session_state.engine
    results = engine.get_data()

    # -----------------------------
    # UI RENDER
    # -----------------------------
    with placeholder.container():

        st.subheader("📊 Institutional Radar (V18)")

        if results:

            st.dataframe(results)

            st.subheader("🚨 Live Signals")

            for r in results:

                ticker = r["ticker"]
                signal = r["signal"]
                score = r["score"]

                msg = f"{ticker} | {signal} | {score}"

                last = st.session_state.last_signal.get(ticker)

                # ALERT ONLY ON STATE CHANGE
                if signal == "HIGH" and last != "HIGH":
                    st.error("🔥 " + msg)
                    send_alert("🔥 " + msg)

                elif signal == "MED":
                    st.warning("⚠️ " + msg)

                st.session_state.last_signal[ticker] = signal

            st.subheader("Top 5 Signals")

            for r in results[:5]:
                st.write(
                    f"{r['ticker']} → {r['signal']} | "
                    f"${r['price']} | Score {r['score']} | "
                    f"RSI {r['RSI']} | Vol {r['volume']}"
                )

        else:
            st.warning("Engine warming up...")

else:
    st.info("Start the engine to begin scanning.")
