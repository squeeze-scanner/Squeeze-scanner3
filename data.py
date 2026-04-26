import yfinance as yf

def get_price_data(ticker):
    df = yf.download(ticker, period="3mo", interval="1d")

    if df is None or df.empty:
        return None

    df = df.reset_index()
    df.columns = [str(c) for c in df.columns]

    return df


def get_short_data(ticker):
    # MOCK DATA (replace later with real API)
    return {
        "short_interest": 0.25,
        "days_to_cover": 6
    }
