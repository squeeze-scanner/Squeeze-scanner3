import numpy as np
import yfinance as yf

# -----------------------------
# HELPERS
# -----------------------------
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
# FAST FILTER (RELAXED - IMPORTANT FIX)
# -----------------------------
def fast_filter(df):
    try:
        if df is None or df.empty or len(df) < 2:
            return None

        close = df["Close"].values
        volume = df["Volume"].values

        price_change = (close[-1] / close[-2]) - 1 if close[-2] != 0 else 0
        vol_ratio = volume[-1] / (np.mean(volume[-20:]) if len(volume) >= 20 else np.mean(volume))

        fast_score = (price_change * 100) + vol_ratio

        # 🔥 FIX: much less strict so universe actually works
        return fast_score if fast_score > -2 else None

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
    if len(v) < 20:
        return 1.0
    avg = np.mean(v[-20:])
    return v[-1] / avg if avg != 0 else 1.0


def momentum(close):
    c = arr(close)
    if len(c) < 20:
        return 0.0
    base = c[-10]
    return (c[-1] / base - 1) if base != 0 else 0.0


def trend_strength(close):
    c = arr(close)
    if len(c) < 30:
        return 0.0
    return (np.mean(c[-10:]) / np.mean(c[-30:])) - 1


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
# SQUEEZE ENGINE (FIXED - NO INFO DEPENDENCY)
# -----------------------------
def squeeze_score(v, vol, br, m, t):
    score = 0

    # volume spike
    if v > 1.5:
        score += 0.25
    elif v > 1.2:
        score += 0.15

    # volatility expansion
    score += min(vol * 0.4, 0.25)

    # breakout
    if br:
        score += 0.2

    # trend + momentum alignment
    score += max(0, m * 0.2)
    score += max(0, t * 0.2)

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

        # fast filter
        if fast_filter(df) is None:
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

        squeeze = squeeze_score(v, vol, br, m, t)

        # -----------------------------
        # BULL / BEAR MODEL
        # -----------------------------
        bull = 0.5
        bear = 0.5

        if r < 30:
            bull += 0.1
        elif r > 70:
            bear += 0.1

        bull += max(0, m * 0.4)
        bear += max(0, -m * 0.4)

        bull += max(0, t * 0.4)
        bear += max(0, -t * 0.4)

        if v > 1.5:
            bull += 0.05

        if br:
            bull += 0.1

        total = bull + bear
        bull /= total
        bear /= total

        confidence = abs(bull - bear)

        # -----------------------------
        # SIGNALS
        # -----------------------------
        if bull > 0.65:
            signal = "BULLISH"
        elif bear > 0.65:
            signal = "BEARISH"
        else:
            signal = "NEUTRAL"

        alerts = []

        if bull > 0.7 and confidence > 0.2:
            alerts.append("🔥 HIGH_BULL_CONFIDENCE")

        if bear > 0.7 and confidence > 0.2:
            alerts.append("🧨 HIGH_BEAR_CONFIDENCE")

        if squeeze > 0.6:
            alerts.append("🚀 HIGH_SQUEEZE_POTENTIAL")

        return {
            "ticker": ticker,
            "price": round(price, 2),

            "bull_prob": round(bull * 100, 1),
            "bear_prob": round(bear * 100, 1),
            "confidence": round(confidence * 100, 1),

            "squeeze_score": round(squeeze * 100, 1),

            "signal": signal,
            "alerts": alerts,

            "RSI": round(r, 2),
            "volume": round(v, 2),
            "momentum": round(m, 4),
            "trend": round(t, 4)
        }

    except:
        return None


def check_signal(ticker):
    return score_stock(ticker)
