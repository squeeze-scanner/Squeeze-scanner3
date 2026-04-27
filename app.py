import streamlit as st
import time
import numpy as np
from scanner import check_signal
from telegram import send_alert

st.title("🚀 V23 Squeeze Radar (FULL TRADE SETUP ENGINE)")

# -----------------------------
# INPUTS
# -----------------------------
user_tickers = st.text_input(
    "➕ Add extra tickers (comma separated)",
    "GME,AMC,TSLA"
)

refresh_rate = st.slider("Refresh interval (seconds)", 5, 60, 15)
start = st.toggle("🟢 Start Scanner")


# -----------------------------
# UNIVERSE
# -----------------------------
def get_full_universe():
    base = [
        "AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA","JPM",
        "V","XOM","PG","MA","HD","CVX","PEP","KO","WMT","BAC"
    ]

    momentum = [
        "PLTR","GME","AMC","BB","NIO","SOFI","RIVN","LCID",
        "AMD","INTC","PYPL","UBER","SQ","SHOP","BABA"
    ]

    return list(set(base + momentum))


def merge_universe(user_input):
    universe = get_full_universe()

    if user_input:
        manual = [t.strip().upper() for t in user_input.split(",") if t.strip()]
        universe.extend(manual)

    return list(set(universe))


# -----------------------------
# TRADE ENGINE (NEW CORE)
# -----------------------------
def build_trade_setup(r):

    price = r.get("price", 0)
    squeeze = r.get("squeeze_score", 0)
    bull = r.get("bull_prob", 50)
    bear = r.get("bear_prob", 50)

    direction = "LONG" if bull > bear else "SHORT"

    # ---------------- ENTRY
    if direction == "LONG":
        entry = price * (1 + (0.002 * (100 - squeeze) / 100))
    else:
        entry = price * (1 - (0.002 * (100 - squeeze) / 100))

    # ---------------- STOP LOSS (volatility proxy)
    stop_distance = price * (0.01 + (squeeze / 1000))  # adaptive risk

    if direction == "LONG":
        stop = price - stop_distance
        target1 = price + (stop_distance * 1.5)
        target2 = price + (stop_distance * 3)
    else:
        stop = price + stop_distance
        target1 = price - (stop_distance * 1.5)
        target2 = price - (stop_distance * 3)

    # ---------------- RISK / REWARD
    risk = abs(price - stop)
    reward = abs(target2 - price)
    rr = reward / risk if risk != 0 else 0

    # ---------------- QUALITY SCORE
    setup_score = (
        squeeze * 0.4 +
        max(bull, bear) * 0.4 +
        (rr * 10)
    )

    if setup_score > 70:
        quality = "A+ SETUP"
    elif setup_score > 55:
        quality = "A SETUP"
    elif setup_score > 40:
        quality = "B SETUP"
    else:
        quality = "C SETUP"

    return {
        "direction": direction,
        "entry": round(entry, 2),
        "stop": round(stop, 2),
        "target_1": round(target1, 2),
        "target_2": round(target2, 2),
        "rr": round(rr, 2),
        "quality": quality
    }


# -----------------------------
# STATE
# -----------------------------
if "cache" not in st.session_state:
    st.session_state.cache = []

if "last_run" not in st.session_state:
    st.session_state.last_run = 0

if "last_alert" not in st.session_state:
    st.session_state.last_alert = {}

if "alerted" not in st.session_state:
    st.session_state.alerted = set()

cooldown = 600
placeholder = st.empty()


# -----------------------------
# MAIN LOOP
# -----------------------------
if start:

    now = time.time()

    if now - st.session_state.last_run >= refresh_rate:

        tickers = merge_universe(user_tickers)[:120]

        results = []

        for t in tickers:
            try:
                res = check_signal(t)
                if res:
                    results.append(res)
            except:
                continue

        results.sort(key=lambda x: x.get("squeeze_score", 0), reverse=True)

        st.session_state.cache = results
        st.session_state.last_run = now

    results = st.session_state.cache

    with placeholder.container():

        st.subheader("📊 Market Radar")
        st.write(f"Active tickers: {len(results)}")

        if results:

            st.dataframe(results)

            st.subheader("🚀 Trade Setups (NEW ENGINE)")

            for r in results:

                setup = build_trade_setup(r)

                ticker = r.get("ticker")
                price = r.get("price")

                msg = (
                    f"{ticker} | {setup['direction']} | {setup['quality']}\n"
                    f"Entry {setup['entry']} | Stop {setup['stop']}\n"
                    f"TP1 {setup['target_1']} | TP2 {setup['target_2']}\n"
                    f"R:R {setup['rr']}"
                )

                score = r.get("squeeze_score", 0)

                is_extreme = score > 70 or setup["rr"] > 3

                last_time = st.session_state.last_alert.get(ticker, 0)

                if is_extreme and now - last_time > cooldown:

                    st.error("🔥 TRADE SETUP: " + msg)
                    send_alert("🔥 TRADE SETUP: " + msg)

                    st.session_state.alerted.add(ticker)
                    st.session_state.last_alert[ticker] = now

                elif setup["quality"] in ["A+", "A"]:
                    st.success(msg)

                elif setup["quality"] == "B SETUP":
                    st.warning(msg)

                else:
                    st.info(msg)

            st.subheader("🏆 Top 10 Candidates")

            for r in results[:10]:
                setup = build_trade_setup(r)

                st.write(
                    f"{r.get('ticker')} | {setup['quality']} | "
                    f"${r.get('price')} | R:R {setup['rr']}"
                )

        else:
            st.info("Scanning market...")
