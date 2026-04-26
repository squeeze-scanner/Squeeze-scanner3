import numpy as np
import yfinance as yf


def arr(x):
    return np.array(x).reshape(-1)


def safe(x, default=0):
    try:
        return float(x)
    except:
        return default


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


def volume_intensity(volume):
    v = arr(volume)
    if len(v) < 20:
        return 1
    avg = np.mean(v[-20:])
    return v[-1] / avg if avg != 0 else 1


def momentum(close):
    c = arr(close)
    if len(c) < 20:
        return 0
    return (c[-1] / c[-10]) - 1


def trend_strength(close):
    c = arr(close)
    if len(c) < 30:
        return 0
    return (np.mean(c[-10:]) / np.mean(c[-30:])) - 1


def volatility(close):
    c = arr(close)
    if len(c) < 20:
        return 0
    m = np.mean(c[-20:])
    return np.std(c[-20:]) / m if m != 0 else 0


def breakout(close):
    c = arr(close)
    if len(c) < 20:
        return False
    return c[-1] > np.max(c[-20:-1])


def score_stock(stock):

    df = stock.history(period="6mo")
    if df is None or df.empty:
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

    if r < 30:
        score += 15
    elif r < 40:
        score += 10

    score += min(v * 10, 25)

    if m > 0.05:
        score += 10
    elif m > 0:
        score += 5

    if t > 0.03:
        score += 10
    elif t > 0:
        score += 5

    if br:
        score += 15

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


def check_signal(ticker):
    try:
        return score_stock(yf.Ticker(ticker))
    except:
        return None
