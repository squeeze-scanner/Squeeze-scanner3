import numpy as np
import yfinance as yf

def arr(x):
    return np.array(x).reshape(-1)

def rsi(close):
    c = arr(close)
    if len(c) < 15:
        return 50

    delta = np.diff(c)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = np.mean(gain[-14:])
    avg_loss = np.mean(loss[-14:]) + 1e-9

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def volume_intensity(volume):
    v = arr(volume)
    if len(v) < 20:
        return 1.0
    return v[-1] / (np.mean(v[-20:]) + 1e-9)


def momentum(close):
    c = arr(close)
    if len(c) < 20:
        return 0.0
    return (c[-1] / c[-10]) - 1


def trend_strength(close):
    c = arr(close)
    if len(c) < 30:
        return 0.0
    return (np.mean(c[-10:]) / np.mean(c[-30:])) - 1


def breakout(close):
    c = arr(close)
    return len(c) > 20 and c[-1] > np.max(c[-20:-1])


def score_stock(ticker):

    try:
        df = yf.Ticker(ticker).history(period="3mo")
        if df is None or len(df) < 30:
            return None

        close = df["Close"].values
        volume = df["Volume"].values
        price = df["Close"].iloc[-1]

        r = rsi(close)
        v = volume_intensity(volume)
        m = momentum(close)
        t = trend_strength(close)
        br = breakout(close)

        # ---------------- BULL / BEAR ----------------
        bull = 0.5
        bear = 0.5

        if r < 35: bull += 0.15
        if r > 65: bear += 0.15

        bull += max(0, m * 0.6)
        bear += max(0, -m * 0.6)

        bull += max(0, t * 0.5)
        bear += max(0, -t * 0.5)

        if v > 1.3: bull += 0.1
        if br: bull += 0.15

        total = bull + bear
        bull /= total
        bear /= total

        confidence = abs(bull - bear)

        # ---------------- SIGNAL FIX ----------------
        if bull > 0.60:
            signal = "BULLISH"
        elif bear > 0.60:
            signal = "BEARISH"
        else:
            signal = "NEUTRAL"

        # ---------------- ALERTS ----------------
        alerts = []

        if bull > 0.70 and confidence > 0.15:
            alerts.append("HIGH_BULL_CONFIDENCE")

        if bear > 0.70 and confidence > 0.15:
            alerts.append("HIGH_BEAR_CONFIDENCE")

        squeeze = v * 0.3 + (1 if br else 0) + abs(m) + abs(t)
        squeeze = min(squeeze / 2, 1.0)

        if squeeze > 0.5:
            alerts.append("HIGH_SQUEEZE_POTENTIAL")

        return {
            "ticker": ticker,
            "price": round(price, 2),
            "signal": signal,
            "bull_prob": round(bull * 100, 1),
            "bear_prob": round(bear * 100, 1),
            "confidence": round(confidence * 100, 1),
            "squeeze_score": round(squeeze * 100, 1),
            "alerts": alerts
        }

    except:
        return None


def check_signal(ticker):
    return score_stock(ticker)
