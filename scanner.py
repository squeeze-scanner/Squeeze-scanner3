import pandas as pd
from ta.momentum import RSIIndicator
from data import get_price_data, get_short_data


# -----------------------------
# SAFE DATA VALIDATION
# -----------------------------
def clean_price_data(df):
    if df is None or df.empty:
        return None

    if 'Close' not in df.columns:
        return None

    df = df.copy()
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df = df.dropna(subset=['Close'])

    if len(df) < 20:
        return None

    return df


# -----------------------------
# RSI CALCULATION
# -----------------------------

import numpy as np

def add_rsi(df):
    close = df['Close']

    # FORCE CLEAN 1D ARRAY
    close = np.array(close).flatten()

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
# SCORING SYSTEM (0–100)
# -----------------------------
def calculate_squeeze_score(rsi, short_interest, days_to_cover):
    score = 0

    # RSI contribution
    if rsi < 25:
        score += 40
    elif rsi < 30:
        score += 30
    elif rsi < 40:
        score += 15

    # Short interest contribution
    if short_interest > 0.30:
        score += 40
    elif short_interest > 0.20:
        score += 25
    elif short_interest > 0.10:
        score += 10

    # Days to cover contribution
    if days_to_cover > 7:
        score += 20
    elif days_to_cover > 5:
        score += 15
    elif days_to_cover > 3:
        score += 5

    return min(score, 100)


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def check_signal(ticker):
    df = get_price_data(ticker)

    df = clean_price_data(df)
    if df is None:
        return None

    df = add_rsi(df)
    if 'RSI' not in df.columns:
        return None

    latest = df.iloc[-1]

    short_data = get_short_data(ticker)
    if not short_data:
        return None

    rsi = latest['RSI']
    short_interest = short_data.get("short_interest", 0)
    days_to_cover = short_data.get("days_to_cover", 0)

    score = calculate_squeeze_score(rsi, short_interest, days_to_cover)

    # Only return meaningful setups
    if score < 50:
        return None

    return {
        "ticker
