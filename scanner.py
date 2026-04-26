import numpy as np
from data import get_price_data, get_short_data


# -----------------------------
# RSI (stable + safe)
# -----------------------------
def calculate_rsi(close):
    close = np.array(close).reshape(-1)

    if len(close) < 10:
        return 50

    delta = np.diff(close)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = np.mean(gain[:14]) if len(gain) >= 14 else np.mean(gain)
    avg_loss = np.mean(loss[:14]) if len(loss) >= 14 else np.mean(loss)

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# -----------------------------
# VOLUME SPIKE (NEW KEY FEATURE)
# -----------------------------
def volume_ratio(volume):
    vol = np.array(volume).reshape(-1)

    if len(vol) < 20:
        return 1

    return vol[-1] / np.mean(vol[-20:])


# -----------------------------
# SCORING ENGINE v2
# -----------------------------
def calculate_score(rsi, short_interest, days_to_cover, vol_ratio):
    score = 0

    # RSI (weak momentum signal)
    if rsi < 50:
        score += 0.5
    if rsi < 40:
        score += 0.5
    if rsi < 30:
        score += 1

    # Short pressure
    if short_interest > 0.25:
        score += 1
    if short_interest > 0.40:
        score += 0.5

    # Days to cover (squeeze fuel)
    if days_to_cover > 5:
        score += 1

    # 🔥 VOLUME SPIKE (IMPORTANT)
    if vol_ratio > 2:
        score += 1.5
    elif vol_ratio > 1.5:
        score += 0.5

    return round(score, 2)


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def check_signal(ticker):
    df = get_price_data(ticker)

    if df is None:
        return None

    close = df["Close"].values
    volume = df["Volume"].values

    rsi = calculate_rsi(close)
    vol_ratio_val = volume_ratio(volume)

    short = get_short_data(ticker)

    score = calculate_score(
        rsi,
        short["short_interest"],
        short["days_to_cover"],
        vol_ratio_val
    )

    return {
        "ticker": ticker,
        "RSI": round(rsi, 2),
        "volume_spike": round(vol_ratio_val, 2),
        "short_interest": short["short_interest"],
        "days_to_cover": short["days_to_cover"],
        "squeeze_score": score
    }
