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
# FAST FILTER
# -----------------------------
def fast_filter(df):
    try:
        if df is None or df.empty or len(df) < 2:
            return None

        close = df["Close"].values
        volume = df["Volume"].values

        price_change = (close[-1] / close[-2]) - 1 if close[-2] != 0 else 0
        vol_ratio = volume[-1] / (np.mean(volume) if np.mean(volume) != 0 else 1)

        fast_score = (price_change * 100) + vol_ratio

        return fast_score if fast_score > 1.2 else None

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
# SHORT DATA
# -----------------------------
def get_short_data(info):
    short_pct = safe(info.get("shortPercentOfFloat"))
    days_cover = safe(info.get("shortRatio"))

    if short_pct is not None:
        short_pct = short_pct * 100

    return short_pct, days_cover


# -----------------------------
# PROBABILITY ENGINE
# -----------------------------
def compute_probabilities(r, v, m, t, vol, br, short_pct, days_cover):

    bullish = 0.50
    bearish = 0.50

    # RSI
    if r < 30:
        bullish += 0.10
    elif r > 70:
        bearish += 0.10

    # momentum
    bullish += max(0, m * 1.5)
    bearish += max(0, -m * 1.5)

    # trend
    bullish += max(0, t * 1.5)
    bearish += max(0, -t * 1.5)

    # volume
    if v > 1.5:
        bullish += 0.05

    # breakout
    if br:
        bullish += 0.10

    # squeeze pressure
    squeeze = 0.0
    if short_pct:
        squeeze += min(short_pct / 100, 0.25)

    if days_cover:
        squeeze += min(days_cover / 20, 0.25)

    total = bullish + bearish
    bullish /= total
    bearish /= total

    return bullish, bearish, squeeze


# -----------------------------
# CORE ENGINE (V26)
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

        try:
            info = stock.info
        except:
            info = {}

        r = rsi(close)
        v = volume_intensity(volume)
        m = momentum(close)
        t = trend_strength(close)
        vol = volatility(close)
        br = breakout(close)

        short_pct, days_cover = get_short_data(info)

        bullish, bearish, squeeze = compute_probabilities(
            r, v, m, t, vol, br, short_pct, days_cover
        )

        confidence = abs(bullish - bearish)

        # -----------------------------
        # SIGNAL LABEL
        # -----------------------------
        if bullish > 0.65:
            signal = "BULLISH"
        elif bearish > 0.65:
            signal = "BEARISH"
        else:
            signal = "NEUTRAL"

        # -----------------------------
        # ALERT FLAGS (NEW V26)
        # -----------------------------
        alerts = []

        if bullish >= 0.70 and confidence >= 0.20:
            alerts.append("🔥 HIGH_BULL_CONFIDENCE")

        if bearish >= 0.70 and confidence >= 0.20:
            alerts.append("🧨 HIGH_BEAR_CONFIDENCE")

        if squeeze >= 0.35:
            alerts.append("🚀 HIGH_SQUEEZE_POTENTIAL")

        return {
            "ticker": ticker,
            "price": round(price, 2),

            "bull_prob": round(bullish * 100, 1),
            "bear_prob": round(bearish * 100, 1),
            "confidence": round(confidence * 100, 1),

            "squeeze_score": round(squeeze * 100, 1),

            "signal": signal,
            "alerts": alerts,

            "RSI": round(r, 2),
            "volume": round(v, 2),
            "momentum": round(m, 4),
            "trend": round(t, 4),

            "short_%": round(short_pct, 2) if short_pct else "N/A",
            "days_to_cover": round(days_cover, 2) if days_cover else "N/A"
        }

    except:
        return None


def check_signal(ticker):
    return score_stock(ticker)
