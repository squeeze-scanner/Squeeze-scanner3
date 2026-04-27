import numpy as np
import yfinance as yf

# -----------------------------
# HELPERS
# -----------------------------
def arr(x):
    return np.array(x).reshape(-1)

def safe(x, default=0.0):
    try:
        return float(x) if x is not None else default
    except:
        return default


# -----------------------------
# FAST FILTER (SAFE + CONSISTENT)
# -----------------------------
def fast_filter(close, volume):

    try:
        if len(close) < 3 or len(volume) < 3:
            return None

        price_change = (close[-1] / close[-2]) - 1 if close[-2] != 0 else 0
        vol_ratio = volume[-1] / (np.mean(volume[-20:]) if len(volume) >= 20 else np.mean(volume))

        fast_score = (price_change * 100) + vol_ratio

        if fast_score < 0.5:   # relaxed threshold = more results
            return None

        return fast_score

    except:
        return None


# -----------------------------
# INDICATORS
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


def volume_intensity(volume):
    v = arr(volume)
    if len(v) < 10:
        return 1.0
    avg = np.mean(v[-10:])
    return v[-1] / avg if avg > 0 else 1.0


def momentum(close):
    c = arr(close)
    if len(c) < 15:
        return 0.0
    return (c[-1] / c[-10]) - 1 if c[-10] != 0 else 0.0


def trend_strength(close):
    c = arr(close)
    if len(c) < 20:
        return 0.0
    return (np.mean(c[-10:]) / np.mean(c[-20:])) - 1


def volatility(close):
    c = arr(close)
    if len(c) < 20:
        return 0.0
    m = np.mean(c[-20:])
    return np.std(c[-20:]) / m if m != 0 else 0.0


def breakout(close):
    c = arr(close)
    if len(c) < 20:
        return False
    return c[-1] > np.max(c[-20:-1])


# -----------------------------
# SYNTHETIC SHORT PRESSURE (IMPORTANT FIX)
# -----------------------------
def synthetic_short_pressure(close, volume):

    c = arr(close)
    v = arr(volume)

    if len(c) < 30:
        return 0.0

    drop = (c[-10] / c[-20] - 1) if c[-20] != 0 else 0
    rebound = (c[-1] / c[-10] - 1) if c[-10] != 0 else 0
    vol_spike = v[-1] / np.mean(v[-20:]) if len(v) >= 20 else 1

    score = 0

    if drop < -0.05:
        score += 30
    if rebound > 0.03:
        score += 25
    if vol_spike > 1.5:
        score += 20

    return min(score, 100)


# -----------------------------
# CORE ENGINE (V27)
# -----------------------------
def score_stock(ticker):

    try:
        stock = yf.Ticker(ticker)

        # ONLY ONE DATA CALL (FAST)
        df = stock.history(period="3mo")

        if df is None or df.empty or len(df) < 30:
            return None

        close = df["Close"].values
        volume = df["Volume"].values

        # FAST FILTER FIRST (cheap)
        if fast_filter(close, volume) is None:
            return None

        price = close[-1]

        # indicators
        r = rsi(close)
        v = volume_intensity(volume)
        m = momentum(close)
        t = trend_strength(close)
        vol = volatility(close)
        br = breakout(close)

        squeeze_pressure = synthetic_short_pressure(close, volume)

        # -----------------------------
        # SCORE
        # -----------------------------
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

        # squeeze pressure boost
        if squeeze_pressure > 70:
            score += 20
        elif squeeze_pressure > 50:
            score += 12
        elif squeeze_pressure > 30:
            score += 6

        score = round(min(score, 100), 2)

        signal = "HIGH" if score >= 65 else "MED" if score >= 45 else "LOW"

        return {
            "ticker": ticker,
            "price": round(float(price), 2),
            "score": score,
            "signal": signal,
            "RSI": round(r, 2),
            "volume": round(v, 2),
            "momentum": round(m, 4),
            "trend": round(t, 4),
            "squeeze_pressure": round(squeeze_pressure, 2)
        }

    except:
        return None


# -----------------------------
# PUBLIC FUNCTION
# -----------------------------
def check_signal(ticker):
    return score_stock(ticker)
