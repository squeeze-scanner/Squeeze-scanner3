from ta.momentum import RSIIndicator
from data import get_price_data, get_short_data

def calculate_rsi(df):
    rsi = RSIIndicator(close=df['Close'], window=14)
    df['RSI'] = rsi.rsi()
    return df

def check_signal(ticker):
    df = get_price_data(ticker)
    df = calculate_rsi(df)

    latest = df.iloc[-1]
    short = get_short_data(ticker)

    if (
        latest['RSI'] < 30 and
        short['short_interest'] > 0.2 and
        short['days_to_cover'] > 5
    ):
        return {
            "ticker": ticker,
            "RSI": round(latest['RSI'], 2),
            "short_interest": short['short_interest'],
            "days_to_cover": short['days_to_cover']
        }

    return None
