import numpy as np
import yfinance as yf


def arr(x):
    return np.array(x).reshape(-1)


def safe(x, default=0.0):
    try:
        if x is None:
            return default
        return float(x)
    except:
        return default


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
# VOLUME
# -----------------------------
def volume_intensity(volume):
    v = arr(volume)

    if len(v) < 20:
        return 1.0

    avg = np.mean(v[-20:])
    return v[-1] / avg if avg > 0 else 1.0


# -----------------------------
# MOMENTUM
# -----------------------------
def momentum(close):
    c = arr(close)

    if len(c) < 20:
        return 0.0

    base = c[-10]
    return (c[-1] / base - 1) if base != 0 else 0.0


# -----------------------------
# TREND
# -----------------------------
def trend_strength(close):
    c = arr(close)

    if len(c) < 30:
        return 0.0

    short = np.mean(c[-10:])
    long = np.mean(c[-30:])

    return (short / long - 1) if long != 0 else 0.0


# -----------------------------
# VOLATILITY
# -----------------------------
def volatility(close):
    c = arr(close)

    if len(c) < 20:
        return 0.0

    m = np.mean(c[-20:])
    return np.std(c[-20:]) / m if m != 0 else 0.0


# -----------------------------
# BREAKOUT
# -----------------------------
def breakout(close):
    c = arr(close)

    if len(c) < 20:
        return False

    return c[-1] > np.max(c[-20:-1])


# -----------------------------
# CORE SCORING ENGINE
# -----------------------------
def score_stock(stock):

    try:
        df = stock.history(period="6mo")

        if df is None or df.empty or len(df) < 30:
            return None

        close = df["Close"].values
        volume = df["Volume"].values

        price = df["Close"].iloc[-1]

        r = rsi(close)
        v = volume_intensity(volume)
        m = momentum(close)
        t = trend_strength(close)
        vol = volatility(close)
        br = breakout(close)

        score = 0

        # RSI
        if r < 30:
            score += 15
        elif r < 40:
            score += 10

        # volume
        score += min(v * 10, 25)

        # momentum
        if m > 0.05:
            score += 10
        elif m > 0:
            score += 5

        # trend
        if t > 0.03:
            score += 10
        elif t > 0:
            score += 5

        # breakout
        if br:
            score += 15

        # volatility
        score += min(vol * 50, 15)

        score = round(min(score, 100), 2)

        signal = "HIGH" if score >= 70 else "MED" if score >= 45 else "LOW"

        return {
            "ticker": stock.ticker,
            "price": safe(price),
            "score": score,
            "signal": signal,
            "RSI": round(r, 2),
            "volume": round(v, 2),
            "momentum": round(m, 4),
            "trend": round(t, 4)
        }

    except:
        return None


# -----------------------------
# PUBLIC CALL
# -----------------------------
def check_signal(ticker):
    try:
        stock = yf.Ticker(ticker)
        return score_stock(stock)
    except:
        return None
