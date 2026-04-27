import numpy as np
import yfinance as yf


def arr(x):
    return np.array(x).reshape(-1)


# -----------------------------
# INDICATORS
# -----------------------------
def rsi(close):
    c = arr(close)
    if len(c) < 15:
        return 50

    delta = np.diff(c)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = np.mean(gain[-14:])
    avg_loss = np.mean(loss[-14:]) + 1e-9

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def volume_intensity(volume):
    v = arr(volume)
    if len(v) < 20:
        return 1.0
    return v[-1] / (np.mean(v[-20:]) + 1e-9)


def momentum(close):
    c = arr(close)
    if len(c) < 20:
        return 0.0
    base = c[-10] if c[-10] != 0 else 1e-9
    return (c[-1] / base) - 1


def trend_strength(close):
    c = arr(close)
    if len(c) < 30:
        return 0.0
    return (np.mean(c[-10:]) / (np.mean(c[-30:]) + 1e-9)) - 1


def breakout(close):
    c = arr(close)
    if len(c) < 20:
        return False
    return c[-1] > np.max(c[-20:-1])


# -----------------------------
# TRADE ENGINE (FIXED V4)
# -----------------------------
def build_trade_plan(price, v, m, t, br):

    volatility = max(abs(m) + abs(t), 0.01)

    entry_low = round(price * (1 - 0.003), 2)
    entry_high = round(price * (1 + 0.003), 2)

    stop = round(price * (1 - (0.012 + volatility * 0.25)), 2)

    # 🔥 FIX: ensure stop NEVER above price
    stop = min(stop, price * 0.995)

    risk = max(price - stop, price * 0.003)

    target1 = round(price + (risk * 1.5), 2)
    target2 = round(price + (risk * 2.5), 2)

    rr = round((target1 - price) / risk, 2)

    # -----------------------------
    # STATE ENGINE
    # -----------------------------
    if price < entry_low:
        state = "WATCHING"
    elif entry_low <= price <= entry_high:
        state = "AT_ENTRY"
    else:
        state = "IN_TREND"

    # -----------------------------
    # TYPE
    # -----------------------------
    if br and v > 1.3:
        setup_type = "BREAKOUT_SQUEEZE"
    elif m > 0.03:
        setup_type = "MOMENTUM"
    elif t > 0.02:
        setup_type = "TREND"
    else:
        setup_type = "REVERSAL"

    return {
        "entry": (entry_low, entry_high),
        "stop": stop,
        "target1": target1,
        "target2": target2,
        "rr": rr,
        "type": setup_type,
        "state": state
    }


# -----------------------------
# CORE ENGINE
# -----------------------------
def score_stock(ticker):

    try:
        df = yf.Ticker(ticker).history(period="3mo")

        if df is None or df.empty or len(df) < 30:
            return None

        close = df["Close"].values
        volume = df["Volume"].values
        price = float(df["Close"].iloc[-1])

        r = rsi(close)
        v = volume_intensity(volume)
        m = momentum(close)
        t = trend_strength(close)
        br = breakout(close)

        # BULL / BEAR
        bull = 0.5
        bear = 0.5

        if r < 35:
            bull += 0.15
        elif r > 65:
            bear += 0.15

        bull += max(0, m * 0.55)
        bear += max(0, -m * 0.55)

        bull += max(0, t * 0.45)
        bear += max(0, -t * 0.45)

        if v > 1.3:
            bull += 0.1

        if br:
            bull += 0.15

        total = bull + bear
        bull /= total
        bear /= total

        confidence = abs(bull - bear)

        if bull > 0.62:
            signal = "BULLISH"
        elif bear > 0.62:
            signal = "BEARISH"
        else:
            signal = "NEUTRAL"

        setup = min(v * 0.3 + abs(m) + abs(t) + (1 if br else 0), 1.0)

        squeeze = min((v * 0.3 + (1 if br else 0) + abs(m) + abs(t)) / 3, 1.0)

        trade_plan = build_trade_plan(price, v, m, t, br)

        return {
            "ticker": ticker,
            "price": round(price, 2),
            "signal": signal,
            "bull_prob": round(bull * 100, 1),
            "bear_prob": round(bear * 100, 1),
            "confidence": round(confidence * 100, 1),
            "squeeze_score": round(squeeze * 100, 1),
            "setup_score": round(setup * 100, 1),
            "score": round((setup * 100 + squeeze * 60 + confidence * 80) / 3, 2),
            "trade_plan": trade_plan
        }

    except Exception as e:
        print("[scanner error]", ticker, e)
        return None


def check_signal(ticker):
    return score_stock(ticker)
