# universe.py

BASE_UNIVERSE = [
    # Mega caps (core liquidity)
    "AAPL","MSFT","NVDA","TSLA","AMZN","META","GOOGL","GOOG",

    # Financial giants
    "JPM","GS","V","MA","BAC","WFC","C","MS",

    # ETFs (market proxy coverage)
    "SPY","QQQ","IWM","DIA","ARKK","XLF","XLK",

    # High volatility / retail momentum
    "PLTR","GME","AMC","BB","NIO","SOFI","RIVN","LCID","COIN",

    # Tech / growth
    "AMD","INTC","NFLX","PYPL","UBER","LYFT","SQ","SHOP","ORCL","CRM","ADBE",

    # Energy / industrial
    "XOM","CVX","BA","CAT",

    # China / global exposure
    "BABA","TSM","NIO","PDD",

    # Defensive / consumer
    "DIS","KO","PEP","WMT","T","VZ"
]


# -----------------------------
# OPTIONAL: DYNAMIC EXPANSION LAYER
# -----------------------------
def get_universe(extra_tickers=None):
    """
    Combines base universe with user input tickers.
    This is your SAFE scalable entry point.
    """

    universe = BASE_UNIVERSE.copy()

    if extra_tickers:
        cleaned = [t.strip().upper() for t in extra_tickers if t.strip()]
        universe.extend(cleaned)

    return list(set(universe))
