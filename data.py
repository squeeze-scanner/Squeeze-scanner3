import yfinance as yf

def get_price_data(ticker):
    df = yf.download(ticker, period="6mo", interval="1d")

    if df is None or df.empty:
        return None

    df = df.reset_index()
    return df


def get_short_data(ticker):
    # MOCK DATA (replace later with real API like Fintel/Ortex)
    return {
        "short_interest": 0.28,
        "days_to_cover": 6
    }
