import numpy as np
from data import get_price_data, get_short_data


# -----------------------------
# SAFE RSI CALCULATION
# -----------------------------
def add_rsi(df):
    if df is None or 'Close' not in df:
        return None

    close = np.array(df['Close']).flatten()

    if len(close) < 15:
        return None

    delta = np.diff(close)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = np.mean(gain[:14])
    avg_loss = np.mean(loss[:14])

    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

    df = df.copy()
    df['RSI'] = [None] * (len(df) - 1) + [rsi]

    return df


# -----------------------------
# SCORING ENGINE (0–3 SCALE)
# -----------------------------
def calculate_score(rsi, short_interest, days_to_cover):
    score = 0

    # RSI condition (oversold = stronger squeeze potential)
    if rsi < 30:
        score += 1
    elif rsi < 45:
        score += 0.5

    # Short interest pressure
    if short_interest > 0.30:
        score += 1
    elif short_interest > 0.20:
        score += 0.5

    # Days to cover (short squeeze fuel)
    if days_to_cover > 7:
        score += 1
    elif days_to_cover > 5:
        score += 0.5

    return score


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def check_signal(ticker):
    df = get_price_data(ticker)

    if df is None:
        return None

    df = add_rsi(df)

    if df is None or 'RSI' not in df:
        return None

    latest = df.iloc[-1]
    short = get_short_data(ticker)

    rsi = latest['RSI']

    if rsi is None:
        return None

    score = calculate_score(
        rsi,
        short["short_interest"],
        short["days_to_cover"]
    )

    # ONLY
