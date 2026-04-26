import numpy as np
import yfinance as yf


# -----------------------------
# SAFE ARRAY
# -----------------------------
def arr(x):
    return np.array(x).reshape(-1)


# -----------------------------
# RSI
# -----------------------------
def rsi(close):
    c = arr(close)

    if len(c) < 15:
        return 50

    delta = np.diff(c)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = np.mean(gain[-14:])
    avg_loss = np.mean(loss[-14:])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# -----------------------------
# VOLUME INTENSITY
# -----------------------------
def volume_intensity(volume):
    v = arr(volume)

    if len(v) < 20:
        return 1

    return v[-1] / np.mean(v[-20:])


# -----------------------------
# BREAKOUT DETECTION
# -----------------------------
def breakout(close):
    c = arr(close)

    if len(c) < 20:
        return False

    return c[-1] > np.max(c[-20:-1])


# -----------------------------
# SHORT + BORROW PRESSURE
# -----------------------------
def short_pressure(info):

    short_pct = info.get("shortPercentOfFloat", 0.05) or 0.05
    short_ratio = info.get("shortRatio", 2) or 2

    return min((short_pct * 5) + (short_ratio / 10), 3)


# -----------------------------
# MARKET REGIME DETECTOR
# -----------------------------
def market_regime(vix_like_volatility):
    if vix_like_volatility > 2.5:
        return "HIGH_VOL"
    elif vix_like_volatility > 1.5:
        return "NORMAL"
    return "LOW_VOL"


# -----------------------------
# CORE SCORING ENGINE
# -----------------------------
def score_stock(stock):

    df = stock.history(period="6mo")

    if df is None or df.empty:
        return None

    close = df["Close"].values
    volume = df["Volume"].values
    info = stock.info

    rsi_val = rsi(close)
    vol = volume_intensity(volume)
    is_breakout = breakout(close)
    short_p = short_pressure(info)

    # -----------------------------
    # V12 SQUEEZE SCORE (0–100)
    # -----------------------------
    score = 0

    # RSI component
    if rsi_val < 30:
        score += 15
    elif rsi_val < 40:
        score += 10

    # volume expansion
    score += min(vol * 10, 30)

    # breakout strength
    if is_breakout:
        score += 15

    # short pressure
    score += short_p * 20

    return {
        "RSI": round(rsi_val, 2),
        "volume_intensity": round(vol, 2),
        "breakout": is_breakout,
        "short_pressure": round(short_p, 2),
        "score": round(min(score, 100), 2)
    }


# -----------------------------
# PUBLIC FUNCTION (V12)
# -----------------------------
def check_signal(ticker):

    stock = yf.Ticker(ticker)

    data = score_stock(stock)

    if data is None:
        return None

    score = data["score"]

    if score >= 70:
        signal = "HIGH"
    elif score >= 45:
        signal = "MED"
    else:
        signal = "LOW"

    return {
        "ticker": ticker,
        "signal": signal,
        **data
    }
