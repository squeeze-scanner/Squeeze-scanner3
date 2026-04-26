import yfinance as yf

def get_price_data(ticker):
    df = yf.download(ticker, period="6mo", interval="1d")

    if df is None or df.empty:
        return None

    df = df.reset_index()
    return df


# -----------------------------
# REALISTIC PROXY SHORT MODEL
# -----------------------------
def get_short_data(ticker):

    stock = yf.Ticker(ticker)
    info = stock.info

    # -----------------------------
    # ATTEMPT REAL FIELDS
    # -----------------------------
    short_percent = info.get("shortPercentOfFloat", None)
    short_ratio = info.get("shortRatio", None)  # days to cover proxy
    float_shares = info.get("floatShares", None)
    shares_out = info.get("sharesOutstanding", None)

    # -----------------------------
    # FALLBACKS (IMPORTANT)
    # -----------------------------
    if short_percent is None:
        short_percent = 0.05  # neutral baseline

    if short_ratio is None:
        short_ratio = 2.0

    # -----------------------------
    # IMPLIED PRESSURE MODEL
    # -----------------------------
    squeeze_pressure = 0

    if float_shares and shares_out:
        float_util = 1 - (float_shares / shares_out)
        squeeze_pressure += max(0, float_util) * 2

    squeeze_pressure += short_percent * 5
    squeeze_pressure += min(short_ratio / 10, 1)

    squeeze_pressure = round(min(squeeze_pressure, 5), 3)

    return {
        "short_interest": round(short_percent, 4),
        "days_to_cover": round(short_ratio, 2),
        "squeeze_pressure": squeeze_pressure
    }
