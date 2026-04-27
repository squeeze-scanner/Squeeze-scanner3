import random
import time

# -----------------------------
# SECTOR UNIVERSE (CLEAN + STRATEGIC)
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

    # 🔥 HIGH PRIORITY (squeeze engine core)
    "MEME": [
        "GME","AMC","BB","KOSS","WISH","NOK","CLOV","MULN",
        "FFIE","HKD","BBBY","ATER","SAVA","WKHS","SPCE","NKLA"
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

    # 🔥 SQUEEZE FUEL (VERY IMPORTANT)
    "HIGH_VOL": [
        "RKLB","ASTS","IONQ","QS","OPEN","RKT","CVNA","TLRY",
        "SNDL","RIOT","MARA","HUT","BITF"
    ]
}

# -----------------------------
# SECTOR STATE (ROTATION MEMORY)
# -----------------------------
_sector_scores = {k: 1.0 for k in SECTORS}
_last_update = 0


# -----------------------------
# SECTOR ROTATION (CONTROLLED TRENDING)
# -----------------------------
def update_sector_weights():
    global _last_update

    now = time.time()

    if now - _last_update < 180:
        return

    for k in _sector_scores:

        drift = random.uniform(0.97, 1.05)

        # bias squeeze-sensitive sectors slightly upward
        if k in ["MEME", "HIGH_VOL"]:
            drift += 0.02

        _sector_scores[k] *= drift

        _sector_scores[k] = max(0.75, min(_sector_scores[k], 2.4))

    _last_update = now


# -----------------------------
# UNIVERSE BUILDER (V28 FIXED)
# -----------------------------
def get_universe(user_input=None, max_size=200):

    update_sector_weights()

    universe = []

    # -----------------------------
    # WEIGHTED SECTOR SAMPLING
    # -----------------------------
    for sector, tickers in SECTORS.items():

        weight = _sector_scores.get(sector, 1.0)

        # stronger floor ensures coverage
        base = 6

        # squeeze bias boost
        if sector in ["MEME", "HIGH_VOL"]:
            base += 4

        bonus = int(weight * 4)

        count = min(len(tickers), base + bonus)

        selected = random.sample(tickers, k=max(2, count))

        universe.extend(selected)

    # -----------------------------
    # USER INPUT BOOST (STRONG PRIORITY)
    # -----------------------------
    if user_input:
        manual = [
            t.strip().upper()
            for t in user_input.split(",")
            if t.strip()
        ]

        # heavy weighting (important for user focus)
        universe.extend(manual * 3)

    # -----------------------------
    # CLEAN + DEDUPE
    # -----------------------------
    universe = list(set(universe))

    # -----------------------------
    # LIQUIDITY PRIORITY BOOST
    # (THIS FIXES "NO HIGH SIGNALS")
    # -----------------------------
    priority_boost = [
        "TSLA","NVDA","AMD","PLTR","COIN","GME","AMC","HOOD","RIVN","SOFI",
        "META","AAPL","MSFT","AMZN","SPY","QQQ"
    ]

    universe.extend(priority_boost)

    universe = list(set(universe))

    # -----------------------------
    # GUARANTEE MINIMUM COVERAGE
    # -----------------------------
    MIN_REQUIRED = 130

    if len(universe) < MIN_REQUIRED:
        for sector in SECTORS.values():
            universe.extend(sector)

    universe = list(set(universe))

    # -----------------------------
    # FINAL ORDERING (LESS RANDOM CHAOS)
    # -----------------------------
    random.shuffle(universe)

    return universe[:max_size]
