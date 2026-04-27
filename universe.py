import random

# -----------------------------
# SECTOR UNIVERSE
# -----------------------------
SECTORS = {
    "TECH": [
        "AAPL","MSFT","NVDA","GOOGL","META","AMZN","AMD","INTC",
        "ADBE","CRM","ORCL","NFLX","PLTR","SNOW","NOW","SHOP",
        "MU","AVGO","QCOM","TXN","AMAT","LRCX"
    ],

    "FINANCE": [
        "JPM","GS","BAC","C","MS","WFC","V","MA","PYPL","AXP","COIN"
    ],

    "MOMENTUM": [
        "TSLA","UBER","LYFT","SQ","HOOD","RIVN","LCID","SOFI",
        "ABNB","DASH","AFRM","UPST","DKNG"
    ],

    "MEME": [
        "GME","AMC","BB","KOSS","WISH","NOK","CLOV","MULN",
        "FFIE","ATER","SAVA","WKHS","SPCE","NKLA"
    ],

    "INDEX": [
        "SPY","QQQ","IWM","DIA","ARKK","VTI","XLF","XLK","SMH"
    ],

    "DEFENSIVE": [
        "XOM","CVX","KO","PEP","WMT","DIS","BA","CAT",
        "MCD","NKE","PG","TGT","HD"
    ],

    "INTERNATIONAL": [
        "BABA","TSM","PDD","JD","TCEHY","NIO","XPEV","LI"
    ],

    "HIGH_VOL": [
        "RKLB","ASTS","IONQ","QS","OPEN","RKT","CVNA","TLRY",
        "SNDL","RIOT","MARA","HUT","BITF"
    ]
}

# -----------------------------
# WEIGHTS
# -----------------------------
SECTOR_WEIGHTS = {
    "TECH": 1.2,
    "FINANCE": 1.0,
    "MOMENTUM": 1.3,
    "MEME": 1.6,
    "INDEX": 0.9,
    "DEFENSIVE": 0.8,
    "INTERNATIONAL": 1.0,
    "HIGH_VOL": 1.7
}

# -----------------------------
# SESSION CACHE (V2 FIX)
# -----------------------------
_cached_universe = None


# -----------------------------
# UNIVERSE BUILDER (V2 STABLE)
# -----------------------------
def get_universe(user_input=None, max_size=200):

    global _cached_universe

    # -----------------------------
    # RETURN SAME UNIVERSE (STABILITY FIX)
    # -----------------------------
    if _cached_universe and not user_input:
        return _cached_universe

    universe = []

    # -----------------------------
    # WEIGHTED SECTOR BUILD (CONTROLLED RANDOMNESS)
    # -----------------------------
    for sector, tickers in SECTORS.items():

        weight = SECTOR_WEIGHTS.get(sector, 1.0)

        base = 6
        bonus = int(weight * 3)

        count = min(len(tickers), base + bonus)

        # deterministic shuffle seed per sector (stable output)
        seeded = tickers.copy()
        random.seed(sector)
        random.shuffle(seeded)

        selected = seeded[:count]

        universe.extend(selected)

    # -----------------------------
    # USER INPUT (HIGH PRIORITY)
    # -----------------------------
    if user_input:
        manual = [
            t.strip().upper()
            for t in user_input.split(",")
            if t.strip()
        ]

        universe.extend(manual * 3)

    # -----------------------------
    # CORE PRIORITY TICKERS
    # -----------------------------
    priority = [
        "TSLA","NVDA","AMD","PLTR","COIN","GME","AMC","HOOD","RIVN","SOFI",
        "META","AAPL","MSFT","AMZN","SPY","QQQ"
    ]

    universe.extend(priority)

    # -----------------------------
    # CLEAN
    # -----------------------------
    universe = list(set(universe))

    # -----------------------------
    # LIMIT
    # -----------------------------
    universe = universe[:max_size]

    # -----------------------------
    # CACHE RESULT (V2 STABILITY)
    # -----------------------------
    _cached_universe = universe

    return universe
