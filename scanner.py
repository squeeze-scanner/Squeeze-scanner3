import numpy as np
import yfinance as yf

# -----------------------------
# HELPERS
# -----------------------------
def arr(x):
    return np.array(x).reshape(-1)


def fast_filter(df):
    try:
        if df is None or df.empty or len(df) < 2:
            return None

        close = df["Close"].values
        volume = df["Volume"].values

        price_change = (close[-1] / close[-2]) - 1 if close[-2] != 0 else 0
        vol_avg = np.mean(volume[-20:]) if len(volume) >= 20 else np.mean(volume)
        vol_ratio = volume[-1] / vol_avg if vol_avg != 0 else 1

        score = (price_change * 100) + vol_ratio

        return score if score > -5 else None

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

    ag = np.mean(gain[-14:])
    al = np.mean(loss[-14:])

    if al == 0:
        return 100

    rs = ag / al
    return 100 - (100 / (1 + rs))


def volume_intensity(volume):
    v = arr(volume)
    if len(v) < 20:
        return 1.0
    return v[-1] / np.mean(v[-20:])


def momentum(close):
    c = arr(close)
    if len(c) < 20:
        return 0.0
    return (c[-1] / c[-10] - 1) if c[-10] != 0 else 0.0


def trend_strength(close):
    c = arr(close)
    if len(c) < 30:
        return 0.0
    return (np.mean(c[-10:]) / np.mean(c[-30:])) - 1


def breakout(close):
    c = arr(close)
    if len(c) < 20:
        return False
    return c[-1] > np.max(c[-20:-1])


# -----------------------------
# SQUEEZE ENGINE
# -----------------------------
def squeeze_score(v, vol, br, m, t):
    score = 0.0

    if v > 1.3:
        score += 0.3
    elif v > 1.1:
        score += 0.2

    score += min(vol * 0.5, 0.3)
    if br:
        score += 0.25

    score += max(0, m * 0.3)
    score += max(0, t * 0.3)

    return min(score, 1.0)


# -----------------------------
# CORE ENGINE
# -----------------------------
def score_stock(ticker):

    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="3mo")

        if df is None or df.empty or len(df) < 30:
            return None

        if fast_filter(df) is None:
            return None

        close = df["Close"].values
        volume = df["Volume"].values
        price = df["Close"].iloc[-1]

        r = rsi(close)
        v = volume_intensity(volume)
        m = momentum(close)
        t = trend_strength(close)
        br = breakout(close)

        squeeze = squeeze_score(v, 0.2, br, m, t)

        # -----------------------------
        # BULL / BEAR MODEL (STRONGER SEPARATION FIX)
        # -----------------------------
        bull = 0.5
        bear = 0.5

        if r < 35:
            bull += 0.15
        elif r > 65:
            bear += 0.15

        bull += max(0, m * 0.6)
        bear += max(0, -m * 0.6)

        bull += max(0, t * 0.5)
        bear += max(0, -t * 0.5)

        if v > 1.3:
            bull += 0.1

        if br:
            bull += 0.15

        total = bull + bear
        bull /= total
        bear /= total

        confidence = abs(bull - bear)

        # -----------------------------
        # SIGNAL FIX (IMPORTANT)
        # -----------------------------
        if bull > 0.58:
            signal = "BULLISH"
        elif bear > 0.58:
            signal = "BEARISH"
        else:
            signal = "NEUTRAL"

        # -----------------------------
        # ALERTS (CLEAR LABELS)
        # -----------------------------
        alerts = []

        if bull >= 0.68:
            alerts.append("BULL_CONFIDENCE")

        if bear >= 0.68:
            alerts.append("BEAR_CONFIDENCE")

        if squeeze >= 0.45:
            alerts.append("SQUEEZE")

        return {
            "ticker": ticker,
            "price": round(price, 2),

            "bull_prob": round(bull * 100, 1),
            "bear_prob": round(bear * 100, 1),
            "confidence": round(confidence * 100, 1),

            "squeeze_score": round(squeeze * 100, 1),

            "signal": signal,
            "alerts": alerts
        }

    except:
        return None


def check_signal(ticker):
    return score_stock(ticker)
