import numpy as np
from data import get_price_data, get_short_data


# -----------------------------
# SAFE SERIES CONVERSION
# -----------------------------
def to_array(x):
    return np.array(x).reshape(-1)


# -----------------------------
# RSI
# -----------------------------
def rsi(close):
    close = to_array(close)

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
# EVENT DETECTORS (CORE v8 CHANGE)
# -----------------------------
def detect_volume_spike(volume):
    v = to_array(volume)
    if len(v) < 20:
        return False, 1

    spike = v[-1] / np.mean(v[-20:])
    return spike > 2.0, spike


def detect_breakout(close):
    c = to_array(close)
    if len(c) < 20:
        return False

    return c[-1] > np.max(c[-20:-1])


def detect_drop_then_rise(close):
    c = to_array(close)
    if len(c) < 15:
        return False

    return (c[-5] < c[-10]) and (c[-1] > c[-5])


# -----------------------------
# MAIN SIGNAL ENGINE (EVENT BASED)
# -----------------------------
def check_signal(ticker):

    df = get_price_data(ticker)

    if df is None:
        return None

    close = df["Close"].values
    volume = df["Volume"].values

    short = get_short_data(ticker)

    rsi_val = rsi(close)

    volume_event, vol_spike = detect_volume_spike(volume)
    breakout_event = detect_breakout(close)
    reversal_event = detect_drop_then_rise(close)

    short_pressure = short["short_interest"] > 0.25
    squeeze_fuel = short["days_to_cover"] > 5

    # -----------------------------
    # EVENT LOGIC (NO RAW SCORE)
    # -----------------------------
    events = []

    if volume_event:
        events.append("VOLUME_SPIKE")

    if breakout_event:
        events.append("BREAKOUT")

    if reversal_event:
        events.append("REVERSAL")

    if short_pressure:
        events.append("HIGH_SHORT_INTEREST")

    if squeeze_fuel:
        events.append("HIGH_DAYS_TO_COVER")

    # -----------------------------
    # SQUEEZE CLASSIFICATION
    # -----------------------------
    if len(events) >= 3:
        signal = "HIGH"
    elif len(events) == 2:
        signal = "MED"
    elif len(events) == 1:
        signal = "LOW"
    else:
        signal = "NONE"

    return {
        "ticker": ticker,
        "signal": signal,
        "events": events,
        "RSI": round(rsi_val, 2),
        "volume_spike": round(vol_spike, 2),
        "short_interest": short["short_interest"],
        "days_to_cover": short["days_to_cover"]
    }
