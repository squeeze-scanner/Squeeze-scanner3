import random
import time

# -----------------------------
# SECTOR MAP
# -----------------------------
SECTORS = {
    "TECH": [
        "AAPL","MSFT","NVDA","GOOGL","META","AMZN","AMD","INTC",
        "ADBE","CRM","ORCL","NFLX","NOW","SNOW","PLTR"
    ],

    "FINANCE": [
        "JPM","GS","BAC","C","MS","WFC","V","MA","PYPL"
    ],

    "MOMENTUM_GROWTH": [
        "TSLA","UBER","LYFT","SHOP","SQ","COIN","HOOD","RIVN","LCID","SOFI"
    ],

    "MEME": [
        "GME","AMC","BB","KOSS","WISH","NOK","CLOV","MULN","FFIE","HKD"
    ],

    "HEAVY_INDEX": [
        "SPY","QQQ","IWM","DIA","ARKK"
    ],

    "COMMODITY_DEFENSIVE": [
        "XOM","CVX","KO","PEP","WMT","DIS","BA","CAT"
    ],

    "INTERNATIONAL": [
        "BABA","TSM","PDD","TCEHY","JD"
    ]
}

# -----------------------------
# SECTOR ROTATION STATE
# -----------------------------
_sector_scores = {
    k: 1.0 for k in SECTORS.keys()
}

_last_update = 0


# -----------------------------
# UPDATE SECTOR WEIGHTS
# -----------------------------
def update_sector_weights():

    global _last_update

    now = time.time()

    # slowly decay rotation influence
    if now - _last_update < 300:
        return

    for k in _sector_scores:
        # random walk bias (simulates “market rotation”)
        _sector_scores[k] *= random.uniform(0.95, 1.08)

        # clamp
        _sector_scores[k] = max(0.5, min(_sector_scores[k], 2.5))

    _last_update = now


# -----------------------------
# BUILD PRIORITY UNIVERSE
# -----------------------------
def get_universe(user_input=None, max_size=120):

    update_sector_weights()

    universe = []

    # -----------------------------
    # WEIGHTED SECTOR SAMPLING
    # -----------------------------
    for sector, tickers in SECTORS.items():

        weight = _sector_scores.get(sector, 1.0)

        # more weight = more tickers selected
        count = int(len(tickers) * weight / 2)

        selected = random.sample(
            tickers,
            k=min(len(tickers), max(2, count))
        )

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
        universe.extend(manual * 2)  # boost importance

    # remove duplicates
    universe = list(set(universe))

    # -----------------------------
    # SHUFFLE + PRIORITY EFFECT
    # -----------------------------
    random.shuffle(universe)

    return universe[:max_size]
