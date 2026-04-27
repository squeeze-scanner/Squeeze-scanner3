import numpy as np
import yfinance as yf


def arr(x):
    return np.array(x).reshape(-1)


# -----------------------------
# INDICATORS (CLEANED + STABLE)
# -----------------------------
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
    base = c[-10] if c[-10] != 0 else 1e-9
    return (c[-1] / base) - 1


def trend_strength(close):
    c = arr(close)
    if len(c) < 30:
        return 0.0
    return (np.mean(c[-10:]) / (np.mean(c[-30:]) + 1e-9)) - 1


def breakout(close):
    c = arr(close)
    if len(c) < 20:
        return False
    return c[-1] > np.max(c[-20:-1])


# -----------------------------
# SQUEEZE + SETUP ENGINE (NEW)
# -----------------------------
def setup_quality(v, m, t, br, r):

    score = 0.0

    # volume expansion
    if v > 1.5:
        score += 0.30
    elif v > 1.2:
        score += 0.20

    # momentum confirmation
    score += min(abs(m) * 0.4, 0.25)

    # trend alignment
    score += min(abs(t) * 0.4, 0.25)

    # breakout confirmation
    if br:
        score += 0.20

    # RSI edge (oversold / overbought extremes)
    if r < 30 or r > 70:
        score += 0.10

    return min(score, 1.0)


# -----------------------------
# CORE SCORING ENGINE
# -----------------------------
def score_stock(ticker):

    try:
        df = yf.Ticker(ticker).history(period="3mo")

        if df is None or df.empty or len(df) < 30:
            return None

        if "Volume" not in df.columns:
            return None

        close = df["Close"].values
        volume = df["Volume"].values
        price = float(df["Close"].iloc[-1])

        # indicators
        r = rsi(close)
        v = volume_intensity(volume)
        m = momentum(close)
        t = trend_strength(close)
        br = breakout(close)

        # -----------------------------
        # BULL / BEAR MODEL (IMPROVED BALANCE)
        # -----------------------------
        bull = 0.5
        bear = 0.5

        if r < 35:
            bull += 0.15
        elif r > 65:
            bear += 0.15

        bull += max(0, m * 0.55)
        bear += max(0, -m * 0.55)

        bull += max(0, t * 0.45)
        bear += max(0, -t * 0.45)

        if v > 1.3:
            bull += 0.1

        if br:
            bull += 0.15

        total = bull + bear
        bull /= total
        bear /= total

        confidence = abs(bull - bear)

        # -----------------------------
        # SIGNAL (CLEAN THRESHOLDING)
        # -----------------------------
        if bull > 0.62:
            signal = "BULLISH"
        elif bear > 0.62:
            signal = "BEARISH"
        else:
            signal = "NEUTRAL"

        # -----------------------------
        # NEW: SETUP QUALITY SCORE
        # -----------------------------
        setup = setup_quality(v, m, t, br, r)

        # squeeze is now REALISTIC (not inflated)
        squeeze = (
            v * 0.3 +
            (1.0 if br else 0.0) +
            abs(m) +
            abs(t)
        ) / 3

        squeeze = min(squeeze, 1.0)

        # -----------------------------
        # ALERTS (BETTER FILTERING)
        # -----------------------------
        alerts = []

        if setup > 0.75 and confidence > 0.15:
            alerts.append("EXTREME_SETUP")

        if setup > 0.60 and squeeze > 0.5:
            alerts.append("STRONG_SETUP")

        if bull > 0.72:
            alerts.append("BULLISH_PRESSURE")

        if bear > 0.72:
            alerts.append("BEARISH_PRESSURE")

        # -----------------------------
        # FINAL SCORE (IMPORTANT UPGRADE)
        # -----------------------------
        score = (
            setup * 100 +
            squeeze * 60 +
            confidence * 80
        ) / 3

        return {
            "ticker": ticker,
            "price": price,

            "signal": signal,

            "bull_prob": round(bull * 100, 1),
            "bear_prob": round(bear * 100, 1),
            "confidence": round(confidence * 100, 1),

            "squeeze_score": round(squeeze * 100, 1),
            "setup_score": round(setup * 100, 1),

            "score": round(score, 2),

            "alerts": alerts
        }

    except Exception as e:
        print(f"[scanner error {ticker}]:", e)
        return None


def check_signal(ticker):
    return score_stock(ticker)
