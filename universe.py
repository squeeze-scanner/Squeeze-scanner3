# universe.py

BASE_UNIVERSE = [
    "AAPL","MSFT","NVDA","TSLA","AMZN","META","GOOGL","GOOG",
    "JPM","GS","V","MA","BAC","WFC","C","MS",
    "SPY","QQQ","IWM","DIA","ARKK","XLF","XLK",
    "PLTR","GME","AMC","BB","NIO","SOFI","RIVN","LCID","COIN",
    "AMD","INTC","NFLX","PYPL","UBER","LYFT","SQ","SHOP","ORCL","CRM","ADBE",
    "XOM","CVX","BA","CAT",
    "BABA","TSM","PDD",
    "DIS","KO","PEP","WMT","T","VZ"
]


# -----------------------------
# MAIN UNIVERSE FUNCTION
# -----------------------------
def get_universe(user_input=None, extra_list=None):
    """
    Returns full scan universe:
    - base market universe
    - plus user input string
    - plus optional list input
    """

    universe = BASE_UNIVERSE.copy()

    # -----------------------------
    # INPUT TYPE 1: STRING (from UI)
    # -----------------------------
    if user_input:
        cleaned = [
            t.strip().upper()
            for t in user_input.split(",")
            if t.strip()
        ]
        universe.extend(cleaned)

    # -----------------------------
    # INPUT TYPE 2: LIST (advanced use)
    # -----------------------------
    if extra_list:
        cleaned = [t.strip().upper() for t in extra_list if t]
        universe.extend(cleaned)

    # remove duplicates
    return list(set(universe))
