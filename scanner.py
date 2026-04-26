import numpy as np
from data import get_price_data, get_short_data


# -----------------------------
# RSI
# -----------------------------
def calculate_rsi(close):
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
# SCORING ENGINE v4 (clean + weighted)
# -----------------------------
def calculate_score(rsi, short_interest, days_to_cover, vol_spike, volat, trend_score):
    score = 0

    # momentum exhaustion
    if rsi < 45:
        score += 0.5
    if rsi < 35:
        score += 0.5

    # short pressure
    if short_interest > 0.25:
        score += 1
    if short_interest > 0.40:
        score += 0.5

    # squeeze fuel
    if days_to_cover > 5:
        score += 1

    # volume spike (VERY IMPORTANT)
    if vol_spike > 2:
        score += 1.5
    elif vol_spike > 1.5:
        score += 0.5

    # volatility expansion
    if volat > 0.03:
        score += 1

    # trend breakout
    if trend_score > 0.05:
        score += 1

    return round(score, 2)


# -----------------------------
# MAIN SCANNER
# -----------------------------
def check_signal(ticker):
    df = get_price_data(ticker)

    if df is None:
        return None

    close = df["Close"].values
    volume = df["Volume"].values

    rsi = calculate_rsi(close)
    vol_spike = volume_spike(volume)
    volat = volatility(close)
    trend_score = trend(close)

    short = get_short_data(ticker)

    score = calculate_score(
        rsi,
        short["short_interest"],
        short["days_to_cover"],
        vol_spike,
        volat,
        trend_score
    )

    return {
        "ticker": ticker,
        "RSI": round(rsi, 2),
        "volume_spike": round(vol_spike, 2),
        "volatility": round(volat, 4),
        "trend": round(trend_score, 4),
        "short_interest": short["short_interest"],
        "days_to_cover": short["days_to_cover"],
        "squeeze_score": score
    }
