import random
import time

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
        "FFIE","HKD","ATER","SAVA","WKHS","SPCE","NKLA"
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
# FIXED SECTOR WEIGHTS (NO RANDOM DRIFT)
# -----------------------------
SECTOR_WEIGHTS = {
    "TECH": 1.2,
    "FINANCE": 1.0,
    "MOMENTUM": 1.3,
    "MEME": 1.6,        # 🔥 core squeeze engine
    "INDEX": 0.9,
    "DEFENSIVE": 0.8,
    "INTERNATIONAL": 1.0,
    "HIGH_VOL": 1.7     # 🔥 volatility engine
}


# -----------------------------
# UNIVERSE BUILDER (STABLE)
# -----------------------------
def get_universe(user_input=None, max_size=200):

    universe = []

    # -----------------------------
    # WEIGHTED SECTOR SELECTION (DETERMINISTIC)
    # -----------------------------
    for sector, tickers in SECTORS.items():

        weight = SECTOR_WEIGHTS.get(sector, 1.0)

        base = 6
        bonus = int(weight * 3)

        count = min(len(tickers), base + bonus)

        selected = random.sample(tickers, k=count)

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
    # PRIORITY CORE TICKERS (ALWAYS PRESENT)
    # -----------------------------
    priority = [
        "TSLA","NVDA","AMD","PLTR","COIN","GME","AMC","HOOD","RIVN","SOFI",
        "META","AAPL","MSFT","AMZN","SPY","QQQ"
    ]

    universe.extend(priority)

    # -----------------------------
    # CLEAN + DEDUPE
    # -----------------------------
    universe = list(set(universe))

    # -----------------------------
    # HARD SIZE LIMIT (PREVENT LAG)
    # -----------------------------
    return universe[:max_size]
