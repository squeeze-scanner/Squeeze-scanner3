import yfinance as yf

def get_price_data(ticker):
    df = yf.download(ticker, period="3mo", interval="1d")

    if df is None or df.empty:
        return None

    # force clean column structure
    df = df.reset_index()

    return df
