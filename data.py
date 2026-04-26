import yfinance as yf

def get_price_data(ticker):
    df = yf.download(ticker, period="3mo", interval="1d")

    if df is None or df.empty:
        return None

    df = df.reset_index()

    # flatten column names (prevents hidden errors)
    df.columns = [str(c) for c in df.columns]

    return df
