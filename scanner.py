from ta.momentum import RSIIndicator
from data import get_price_data, get_short_data

def calculate_rsi(df):
    if df is None or 'Close' not in df:
        return None

    close = df['Close']

    # FORCE 1D SERIES CLEANUP
    close = close.squeeze()

    if close.isnull().all():
        return None

    rsi = RSIIndicator(close=close, window=14)
    df['RSI'] = rsi.rsi()

    return df
