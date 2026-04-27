import random
import time

# -----------------------------
# EXPANDED SECTOR UNIVERSE (CLEAN + REALISTIC)
# -----------------------------
SECTORS = {
    # ---------------- TECH (core + AI + growth)
    "TECH": [
        "AAPL","MSFT","NVDA","GOOGL","META","AMZN","AMD","INTC",
        "ADBE","CRM","ORCL","NFLX","PLTR","SNOW","NOW","SHOP",
        "MU","AVGO","QCOM","TXN","AMAT","LRCX"
    ],

    # ---------------- FINANCE (liquidity engines)
    "FINANCE": [
        "JPM","GS","BAC","C","MS","WFC","V","MA","PYPL","AXP","COIN"
    ],

    # ---------------- MOMENTUM / RETAIL FLOW
    "MOMENTUM": [
        "TSLA","UBER","LYFT","SQ","HOOD","RIVN","LCID","SOFI",
        "ABNB","DASH","AFRM","UPST","DKNG"
    ],

    # ---------------- MEME / HIGH SHORT INTEREST ZONE
    "MEME": [
        "GME","AMC","BB","KOSS","WISH","NOK","CLOV","MULN",
        "FFIE","HKD","BBBY","ATER","SAVA","WKHS","SPCE","NKLA"
    ],

    # ---------------- INDEX / ETF FLOW
    "INDEX": [
        "SPY","QQQ","IWM","DIA","ARKK","VTI","XLF","XLK","SMH"
    ],

    # ---------------- DEFENSIVE / HEDGE FLOW
    "DEFENSIVE": [
        "XOM","CVX","KO","PEP","WMT","DIS","BA","CAT",
        "MCD","NKE","PG","TGT","HD"
    ],

    # ---------------- INTERNATIONAL / GLOBAL FLOW
    "INTERNATIONAL": [
        "BABA","TSM","PDD","JD","TCEHY","NIO","XPEV","LI"
    ],

    # ---------------- HIGH VOLATILITY SMALL CAPS (SQUEEZE FUEL)
    "HIGH_VOL": [
        "RKLB","ASTS","IONQ","QS","OPEN","RKT","CVNA","TLRY",
        "SNDL","RIOT","MARA","HUT","BITF"
    ]
}

# -----------------------------
# SECTOR ROTATION STATE
# -----------------------------
_sector_scores = {k: 1.0 for k in SECTORS}
_last_update = 0


# -----------------------------
# ROTATION ENGINE (SMOOTH + NON-RANDOM CRASH PREVENTION)
# -----------------------------
def update_sector_weights():
    global _last_update

    now = time.time()

    # update every 3 minutes
    if now - _last_update < 180:
        return

    for k in _sector_scores:

        drift = random.uniform(0.96, 1.05)

        _sector_scores[k] *= drift

        # clamp (prevents explosion or decay)
        _sector_scores[k] = max(0.7, min(_sector_scores[k], 2.3))

    _last_update = now


# -----------------------------
# CORE UNIVERSE BUILDER (V27 FIXED)
# -----------------------------
def get_universe(user_input=None, max_size=200):

    update_sector_weights()

    universe = []

    # -----------------------------
    # WEIGHTED SECTOR EXPANSION
    # (ENSURES FULL MARKET COVERAGE)
    # -----------------------------
    for sector, tickers in SECTORS.items():

        weight = _sector_scores.get(sector, 1.0)

        # GUARANTEED MINIMUM PER SECTOR
        base = 5

        # dynamic boost
        bonus = int(weight * 4)

        count = min(len(tickers), base + bonus)

        # safe sampling (no crashes if small list)
        selected = random.sample(tickers, k=max(1, count))

        universe.extend(selected)

    # -----------------------------
    # USER INPUT BOOST (HIGHEST PRIORITY)
    # -----------------------------
    if user_input:
        manual = [
            t.strip().upper()
            for t in user_input.split(",")
            if t.strip()
        ]

        # strong weighting (important for scanner focus)
        universe.extend(manual)
        universe.extend(manual)
        universe.extend(manual[:10])

    # -----------------------------
    # CLEANUP
    # -----------------------------
    universe = list(set(universe))

    # -----------------------------
    # GUARANTEE MINIMUM COVERAGE
    # (FIXES "18 TICKERS BUG")
    # -----------------------------
    MIN_REQUIRED = 120

    if len(universe) < MIN_REQUIRED:

        flat = []
        for sector in SECTORS.values():
            flat.extend(sector)

        # fill aggressively
        universe.extend(flat)
        universe.extend(flat[:50])

    universe = list(set(universe))

    # -----------------------------
    # FINAL ORDERING (SLIGHT STRUCTURE, NOT PURE RANDOM)
    # -----------------------------
    random.shuffle(universe)

    return universe[:max_size]
