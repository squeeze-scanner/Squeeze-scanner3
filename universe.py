# universe.py
import random

# -----------------------------
# CORE MARKET (LIQUID)
# -----------------------------
CORE = [
    "AAPL","MSFT","NVDA","TSLA","AMZN","META","GOOGL","GOOG",
    "JPM","GS","V","MA","BAC","WFC","C","MS",
    "SPY","QQQ","IWM","DIA","ARKK","XLF","XLK",
    "AMD","INTC","NFLX","PYPL","ORCL","CRM","ADBE",
    "XOM","CVX","BA","CAT",
    "BABA","TSM","PDD",
    "DIS","KO","PEP","WMT","T","VZ"
]

# -----------------------------
# VOLATILITY / GROWTH
# -----------------------------
VOLATILITY = [
    "PLTR","SOFI","RIVN","LCID","COIN","HOOD",
    "SNAP","ROKU","AFRM","UPST","DKNG","NET",
    "CRWD","ZS","PANW","MDB","SNOW","DDOG",
    "SHOP","SQ","UBER","LYFT","ABNB"
]

# -----------------------------
# MEME / RETAIL FLOW
# -----------------------------
MEME = [
    "GME","AMC","BB","KOSS","EXPR","BYND","TLRY",
    "SNDL","WISH","NOK","CLOV","WKHS","SPCE",
    "MARA","RIOT","BBBY","HKD","MULN","FFIE",
    "APRN","CEI","TRKA","AI","IONQ","QS"
]

# -----------------------------
# UNIVERSE BUILDER (SMART)
# -----------------------------
def get_universe(user_input=None, max_size=100):

    # combine all pools
    universe = CORE + VOLATILITY + MEME

    # -----------------------------
    # USER INPUT
    # -----------------------------
    if user_input:
        manual = [
            t.strip().upper()
            for t in user_input.split(",")
            if t.strip()
        ]
        universe.extend(manual)

    # remove duplicates
    universe = list(set(universe))

    # -----------------------------
    # 🔥 RANDOM ROTATION (KEY FEATURE)
    # -----------------------------
    random.shuffle(universe)

    # -----------------------------
    # LIMIT SIZE (CRITICAL FOR SPEED)
    # -----------------------------
    return universe[:max_size]
