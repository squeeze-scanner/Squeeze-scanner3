import numpy as np
from data import get_price_data, get_short_data


# -----------------------------
# RSI (stable)
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
# CORE SIGNALS
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
# NORMALISATION (IMPORTANT v5 CHANGE)
# -----------------------------
def normalize(value, min_v, max_v):
    return max(0, min(1, (value - min_v) / (max_v - min_v)))


# -----------------------------
# SQUEEZE PRESSURE MODEL (v5 CORE)
# -----------------------------
def squeeze_pressure(rsi, short_interest, days_to_cover, vol_spike, volat, trend_score):

    # normalize signals (0–1 range)
    rsi_score = normalize(50 - rsi, 0, 50)
    short_score = normalize(short_interest, 0.1, 0.5)
    dtc_score = normalize(days_to_cover, 2, 10)
    vol_score = normalize(vol_spike, 1, 3)
    volat_score = normalize(volat, 0.01, 0.06)
    trend_score = normalize(trend_score, 0, 0.1)

    # weighted model (IMPORTANT CHANGE)
    score = (
        rsi_score * 1.2 +
        short_score * 2.0 +
        dtc_score * 1.5 +
        vol_score * 1.8 +
        volat_score * 1.0 +
        trend_score * 1.5
    )

    return round(score * 5, 2)  # scale to ~0–10


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def check_signal(ticker):
    df = get_price_data(ticker)

    if df is None:
        return None

    close = df["Close"].values
    volume = df["Volume"].values

    rsi_val = rsi(close)
    vol_spike_val = volume_spike(volume)
    volat_val = volatility(close)
    trend_val = trend(close)

    short = get_short_data(ticker)

    score = squeeze_pressure(
        rsi_val,
        short["short_interest"],
        short["days_to_cover"],
        vol_spike_val,
        volat_val,
        trend_val
    )

    # 🚨 ALERT LEVEL
    alert = "LOW"
    if score > 6:
        alert = "HIGH"
    elif score > 4:
        alert = "MED"

    return {
        "ticker": ticker,
        "squeeze_score": score,
        "alert": alert,
        "RSI": round(rsi_val, 2),
        "volume_spike": round(vol_spike_val, 2),
        "volatility": round(volat_val, 4),
        "trend": round(trend_val, 4),
        "short_interest": short["short_interest"],
        "days_to_cover": short["days_to_cover"]
    }
