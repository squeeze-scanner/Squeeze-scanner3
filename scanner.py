import numpy as np
from data import get_price_data, get_short_data


# -----------------------------
# SIMPLE RSI (NO LIBRARIES)
# -----------------------------
def calculate_rsi(close):
    close = np.array(close).flatten()

    if len(close) < 15:
        return None

    delta = np.diff(close)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = np.mean(gain[:14])
    avg_loss = np.mean(loss[:14])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


# -----------------------------
# SCORING ENGINE (0–3 SCALE)
# -----------------------------
def calculate_score(rsi, short_interest, days_to_cover, volume_ratio):
    score = 0

    if rsi < 50:
        score += 1
    if rsi < 40:
        score += 1

    if short_interest > 0.25:
        score += 1

    if days_to_cover > 5:
        score += 1

    # 🔥 THIS IS WHAT YOU'RE MISSING
    if volume_ratio > 1.5:
        score += 1

    return score

# -----------------------------
# MAIN FUNCTION
# -----------------------------
def check_signal(ticker):
    df = get_price_data(ticker)

    if df is None or 'Close' not in df:
        return None

    close = df['Close'].dropna()
    rsi = calculate_rsi(close)

    if rsi is None:
        return None

    short = get_short_data(ticker)

    score = calculate_score(
        rsi,
        short["short_interest"],
        short["days_to_cover"]
    )

    # 🔥 ALWAYS RETURN DATA (NO FILTERING)
    return {
        "ticker": ticker,
        "RSI": round(float(rsi), 2),
        "short_interest": short["short_interest"],
        "days_to_cover": short["days_to_cover"],
        "squeeze_score": round(score, 2)
    }
