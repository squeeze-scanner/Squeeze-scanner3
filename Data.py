import yfinance as yf

def get_price_data(ticker):
    return yf.download(ticker, period="3mo", interval="1d")

def get_short_data(ticker):
    return {
        "short_interest": 0.25,
        "days_to_cover": 6
    }
