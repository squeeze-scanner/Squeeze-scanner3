import yfinance as yf


BASE_UNIVERSE = [
    "AAPL","MSFT","NVDA","TSLA","AMZN","META","AMD","GOOGL",
    "PLTR","GME","AMC","BB","NIO","SOFI","SPY","QQQ","IWM",
    "BABA","NFLX","INTC","PYPL","UBER","LYFT","COIN"
]


def discover_movers():
    movers = []

    for t in BASE_UNIVERSE:
        try:
            df = yf.Ticker(t).history(period="5d")

            if df is None or df.empty:
                continue

            volume_ratio = df["Volume"].iloc[-1] / df["Volume"].mean()
            price_change = abs(df["Close"].iloc[-1] / df["Close"].iloc[-2] - 1)

            # 🔥 PRE-FILTER (this is key)
            if volume_ratio > 1.5 or price_change > 0.03:
                movers.append(t)

        except:
            continue

    return list(set(movers))
