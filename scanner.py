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

    avg = np.mean(v[-20:])
    if avg == 0:
        return 1

    return v[-1] / avg


# -----------------------------
# MOMENTUM
# -----------------------------
def momentum(close):
    c = arr(close)

    if len(c) < 20:
        return 0

    return (c[-1] / c[-10]) - 1


# -----------------------------
# TREND STRENGTH
# -----------------------------
def trend_strength(close):
    c = arr(close)

    if len(c) < 30:
        return 0

    short_ma = np.mean(c[-10:])
    long_ma = np.mean(c[-30:])

    if long_ma == 0:
        return 0

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
# SHORT PRESSURE (SAFE)
# -----------------------------
def
