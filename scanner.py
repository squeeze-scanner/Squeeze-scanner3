import numpy as np
import yfinance as yf


# -----------------------------
# SAFE ARRAY
# -----------------------------
def arr(x):
    return np.array(x).reshape(-1)


# -----------------------------
# RSI (simple + stable)
# -----------------------------
def rsi(close):
    close = arr(close)

    if len(close) < 15:
        return 50

    delta = np.diff(close)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = np.mean(gain[-14:])
    avg_loss = np.mean(loss[-14:])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# -----------------------------
# VOLUME SPIKE
# -----------------------------
def volume_spike(volume):
    v = arr(volume)
    if len(v) < 20:
        return 1, False

    spike = v[-1] / np.mean(v[-20:])
    return spike, spike > 2.0


# -----------------------------
# BREAKOUT DETECTION
# -----------------------------
def breakout(close):
    c = arr(close)
    if len(c) < 20:
        return False

    return c[-1] > np.max(c[-20:-1])


# -----------------------------
# OPTIONS GAMMA PROXY
# -----------------------------
def gamma_proxy(stock):
    try:
        opt = stock.options
        if not opt:
            return 0

        nearest = opt[0]
        chain = stock.option_chain(nearest)

        calls_oi = chain.calls["openInterest"].sum()
        puts_oi = chain.puts["openInterest"].sum()

        total = calls_oi + puts_oi

        if total == 0:
            return 0

        # call dominance = bullish gamma pressure proxy
        return calls_oi / total

    except:
        return 0


# -----------------------------
# SHORT PRESSURE MODEL
# -----------------------------
def short_pressure(info):

    short_pct = info.get("shortPercentOfFloat", 0.05) or 0.05
    short_ratio = info.get("shortRatio", 2) or 2

    pressure = 0
    pressure += short_pct * 5
    pressure += min(short_ratio / 10, 1)

    return min(pressure, 3)


# -----------------------------
# MAIN ENGINE (V11)
# -----------------------------
def check_signal(ticker):

    stock = yf.Ticker(ticker)
    df = stock.history(period="6mo")

    if df is None or df.empty:
        return None

    close = df["Close"].values
    volume = df["Volume"].values

    info = stock.info

    # -----------------------------
    # CORE METRICS
    # -----------------------------
    rsi_val = rsi(close)
    vol_spike, is_spike = volume_spike(volume)
    is_breakout = breakout(close)

    gamma = gamma_proxy(stock)
    short_p = short_pressure(info)

    # -----------------------------
    # SQUEEZE SCORE (0–100)
    # -----------------------------
    score = 0

    # RSI contribution
    if rsi_val < 30:
        score += 15
    elif rsi_val < 40:
        score += 10

    # volume
    score += min(vol_spike * 10, 25)

    # breakout
    if is_breakout:
        score += 15

    # gamma squeeze pressure
    score += gamma * 25

    # short pressure
    score += short_p * 20

    score = round(min(score, 100), 2)

    # -----------------------------
    # SIGNAL CLASSIFICATION
    # -----------------------------
    if score >= 70:
        signal = "HIGH"
    elif score >= 45:
        signal = "MED"
    else:
        signal = "LOW"

    return {
        "ticker": ticker,
        "signal": signal,
        "squeeze_score": score,
        "RSI": round(rsi_val, 2),
        "volume_spike": round(vol_spike, 2),
        "gamma_pressure": round(gamma, 2),
        "short_pressure": round(short_p, 2),
        "breakout": is_breakout
    }
