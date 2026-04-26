import numpy as np
from data import get_price_data, get_short_data


# -----------------------------
# RSI (stable baseline)
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
# VOLATILITY (NEW v3 SIGNAL)
# -----------------------------
def volatility(close):
    close = np.array(close).reshape(-1)

    if len(close) < 10:
        return 0

    return np.std(close[-20:]) / np.mean(close[-20:])


# -----------------------------
# VOLUME SPIKE (REFINED)
# -----------------------------
def volume_ratio(volume):
    vol = np.array(volume).reshape(-1)

    if len(vol) < 20:
        return 1

    return vol[-1] / np.mean(vol[-20:])


# -----------------------------
# SCORE ENGINE v3
# -----------------------------
def calculate_score(rsi, short_interest, days_to_cover, vol_ratio, volat):
    score = 0

    # Momentum (weaker weight than before)
    if rsi < 45:
        score += 0.5
    if rsi < 35:
        score += 0.5

    # Short pressure (still important)
    if short_interest > 0.25:
        score += 1
    if short_interest > 0.40:
        score += 0.5

    # Squeeze fuel
    if days_to_cover > 5:
        score += 1

    # 🔥 Volume spike (critical)
    if vol_ratio > 2:
        score += 1.5
    elif vol_ratio > 1.5:
        score += 0.5

    # 🔥 Volatility (new squeeze trigger)
    if volat > 0.03:
        score += 1
    elif volat > 0.02:
        score += 0.5

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
    vol_ratio_val = volume_ratio(volume)
    volat_val = volatility(close)

    short = get_short_data(ticker)

    score = calculate_score(
        rsi,
        short["short_interest"],
        short["days_to_cover"],
        vol_ratio_val,
        volat_val
    )

    return {
        "ticker": ticker,
        "RSI": round(rsi, 2),
        "volume_spike": round(vol_ratio_val, 2),
        "volatility": round(volat_val, 4),
        "short_interest": short["short_interest"],
        "days_to_cover": short["days_to_cover"],
        "squeeze_score": score
    }
