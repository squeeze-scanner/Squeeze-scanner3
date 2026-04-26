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
# VOLUME INTENSITY (STABLE)
# -----------------------------
def volume_intensity(volume):
    v = arr(volume)

    if len(v) < 20:
        return 1

    avg = np.mean(v[-20:])
    if avg == 0:
        return 1

    return v[-1] / avg


# -----------------------------
# MOMENTUM (STABILIZED)
# -----------------------------
def momentum(close):
    c = arr(close)

    if len(c) < 20:
        return 0

    # smoother momentum (less noise)
    return (c[-1] / c[-10]) - 1


# -----------------------------
# TREND STRENGTH (NEW - IMPORTANT)
# -----------------------------
def trend_strength(close):
    c = arr(close)

    if len(c) < 30:
        return 0

    short_ma = np.mean(c[-10:])
    long_ma = np.mean(c[-30:])

    return (short_ma / long_ma) - 1


# -----------------------------
# BREAKOUT
# -----------------------------
def breakout(close):
    c = arr(close)

    if len(c) < 20:
        return False

    return c[-1] > np.max(c[-20:-1])


# -----------------------------
# SHORT PRESSURE (ROBUSTED)
# -----------------------------
def short_pressure(info):

    short_pct = info.get("shortPercentOfFloat", None)
    short_ratio = info.get("shortRatio", None)

    score = 0

    if short_pct:
        score += short_pct * 5
    else:
        score += 0.4  # safer baseline

    if short_ratio:
        score += min(short_ratio / 10, 1)

    return min(score, 3)


# -----------------------------
# VOLATILITY
# -----------------------------
def volatility(close):
    c = arr(close)

    if len(c) < 20:
        return 0

    return np.std(c[-20:]) / np.mean(c[-20:])


# -----------------------------
# CORE ENGINE (V14.1)
# -----------------------------
def score_stock(stock):

    df = stock.history(period="6mo")

    if df is None or df.empty:
        return None

    close = df["Close"].values
    volume = df["Volume"].values
    info = stock.info

    latest_price = df["Close"].iloc[-1]

    rsi_val = rsi(close)
    vol = volume_intensity(volume)
    mom = momentum(close)
    trend = trend_strength(close)
    is_breakout = breakout(close)
    short_p = short_pressure(info)
    volat = volatility(close)

    # -----------------------------
    # SCORE (0–100)
    # -----------------------------
    score = 0

    # RSI
    if rsi_val < 30:
        score += 15
    elif rsi_val < 40:
        score += 10

    # volume
    score += min(vol * 10, 25)

    # momentum (smoothed)
    if mom > 0.05:
        score += 10
    elif mom > 0:
        score += 5

    # trend alignment (NEW)
    if trend > 0.03:
        score += 10
    elif trend > 0:
        score += 5

    # breakout
    if is_breakout:
        score += 15

    # short pressure
    score += short_p * 20

    # volatility
    score += min(volat * 50, 15)

    score = round(min(score, 100), 2)

    # -----------------------------
    # SIGNAL
