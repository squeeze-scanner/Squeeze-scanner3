import numpy as np
from data import get_price_data, get_short_data


# -----------------------------
# RSI (safe + fallback)
# -----------------------------
def rsi(close):
    close = np.array(close).reshape(-1)

    if len(close) < 10:
        return 50

    delta = np.diff(close)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = np.mean(gain[-14:]) if len(gain) >= 14 else np.mean(gain)
    avg_loss = np.mean(loss[-14:]) if len(loss) >= 14 else np.mean(loss)

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# -----------------------------
# FEATURES
# -----------------------------
def volume_spike(volume):
    v = np.array(volume).reshape(-1)

    if len(v) < 20:
        return 1

    return v[-1] / np.mean(v[-20:])


def volatility(close):
    c = np.array(close).reshape(-1)

    if len(c) < 20:
        return 0

    return np.std(c[-20:]) / np.mean(c[-20:])


def trend(close):
    c = np.array(close).reshape(-1)

    if len(c) < 10:
        return 0

    return (c[-1] - c[-10]) / c[-10]


# -----------------------------
# SCORE ENGINE
# -----------------------------
def squeeze_score(rsi_val, short_interest, days_to_cover, vol_spike, volat, trend_val):

    score = 0

    # RSI pressure
    if rsi_val < 45:
        score += 0.5
    if rsi_val < 35:
        score += 0.5

    # Short interest (mock but structured)
    if short_interest > 0.25:
        score += 1
    if short_interest > 0.40:
        score += 0.5

    # Days to cover
    if days_to_cover > 5:
        score += 1

    # Volume spike
    if vol_spike > 2:
        score += 1.5
    elif vol_spike > 1.5:
        score += 0.5

    # Volatility
    if volat > 0.03:
        score += 1

    # Trend strength
    if trend_val > 0.05:
        score += 1

    return round(score, 2)


# -----------------------------
# MAIN FUNCTION (100% SAFE OUTPUT)
# -----------------------------
def check_signal(ticker):

    try:
        df = get_price_data(ticker)

        # SAFE fallback (never return None)
        if df is None or "Close" not in df or "Volume" not in df:
            return {
                "ticker": ticker,
                "squeeze_score": 0,
                "alert": "LOW",
                "RSI": 50,
                "volume_spike": 1,
                "volatility": 0,
                "trend": 0,
                "short_interest": 0.28,
                "days_to_cover": 6
            }

        close = np.array(df["Close"]).reshape(-1)
        volume = np.array(df["Volume"]).reshape(-1)

        rsi_val = rsi(close)
        vol_spike_val = volume_spike(volume)
        volat_val = volatility(close)
        trend_val = trend(close)

        short = get_short_data(ticker)

        score = squeeze_score(
            rsi_val,
            short["short_interest"],
            short["days_to_cover"],
            vol_spike_val,
            volat_val,
            trend
