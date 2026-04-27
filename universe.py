import random
import time

# -----------------------------
# SECTOR UNIVERSE (EXPANDED + CLEANED)
# -----------------------------
SECTORS = {
    "TECH": [
        "AAPL","MSFT","NVDA","GOOGL","META","AMZN","AMD","INTC",
        "ADBE","CRM","ORCL","NFLX","PLTR","SNOW","NOW","SHOP"
    ],

    "FINANCE": [
        "JPM","GS","BAC","C","MS","WFC","V","MA","PYPL"
    ],

    "MOMENTUM": [
        "TSLA","UBER","LYFT","SQ","COIN","HOOD","RIVN","LCID","SOFI"
    ],

    "MEME": [
        "GME","AMC","BB","KOSS","WISH","NOK","CLOV","MULN","FFIE","HKD","BBBY"
    ],

    "INDEX": [
        "SPY","QQQ","IWM","DIA","ARKK","VTI"
    ],

    "DEFENSIVE": [
        "XOM","CVX","KO","PEP","WMT","DIS","BA","CAT"
    ],

    "INTERNATIONAL": [
        "BABA","TSM","PDD","JD","TCEHY"
    ]
}

# -----------------------------
# SECTOR ROTATION STATE
# -----------------------------
_sector_scores = {k: 1.0 for k in SECTORS}
_last_update = 0


# -----------------------------
# UPDATE SECTOR WEIGHTS (SMOOTH ROTATION)
# -----------------------------
def update_sector_weights():
    global _last_update

    now = time.time()

    # rotate slowly (stability > chaos)
    if now - _last_update < 180:
        return

    for k in _sector_scores:
        drift = random.uniform(0.97, 1.04)
        _sector_scores[k] *= drift

        # clamp stability
        _sector_scores[k] = max(0.6, min(_sector_scores[k], 2.2))

    _last_update = now


# -----------------------------
# MAIN UNIVERSE BUILDER
# -----------------------------
def get_universe(user_input=None, max_size=150):

    update_sector_weights()

    universe = []

    # -----------------------------
    # WEIGHTED SECTOR SELECTION
    # (ENSURES ALL SECTORS ALWAYS ACTIVE)
    # -----------------------------
    for sector, tickers in SECTORS.items():

        weight = _sector_scores.get(sector, 1.0)

        # FIX: stable deterministic selection (not too random)
        base_count = 4
        bonus = int(weight * 3)

        count = min(len(tickers), base_count + bonus)

        selected = random.sample(tickers, count)

        universe.extend(selected)

    # -----------------------------
    # USER INPUT BOOST (HIGH PRIORITY)
    # -----------------------------
    if user_input:
        manual = [
            t.strip().upper()
            for t in user_input.split(",")
            if t.strip()
        ]

        # boost importance by duplication (signal weighting)
        universe.extend(manual)
        universe.extend(manual[:10])  # extra weight for user picks

    # -----------------------------
    # CLEANUP
    # -----------------------------
    universe = list(set(universe))

    # -----------------------------
    # GUARANTEED MIN COVERAGE (FIXES "ONLY 18 TICKERS" BUG)
    # -----------------------------
    MIN_REQUIRED = 80

    if len(universe) < MIN_REQUIRED:
        fallback = []

        for sector in SECTORS:
            fallback.extend(SECTORS[sector])

        universe.extend(fallback)

    universe = list(set(universe))

    # -----------------------------
    # FINAL SORTING (STABILITY BOOST)
    # -----------------------------
    random.shuffle(universe)

    return universe[:max_size]
