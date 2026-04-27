import numpy as np

# -----------------------------
# SAFE IMPORT (CRITICAL FIX)
# -----------------------------
try:
    import yfinance as yf
except Exception as e:
    print("[WARN] yfinance import failed:", e)
    yf = None


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
# TRADE ENGINE
# -----------------------------
def build_trade_plan(price, v, m, t, br):

    volatility = max(abs(m) + abs(t), 0.01)

    entry_low = round(price * (1 - 0.003), 2)
    entry_high = round(price * (1 + 0.003), 2)

    stop = round(price * (1 - (0.012 + volatility * 0.25)), 2)
    stop = min(stop, price * 0.995)

    risk = max(price - stop, price * 0.003)

    target1 = round(price + (risk * 1.5), 2)
    target2 = round(price + (risk * 2.5), 2)

    rr = round((target1 - price) / risk, 2)

    if price < entry_low:
        state = "WATCHING"
    elif entry_low <= price <= entry_high:
        state = "AT_ENTRY"
    else:
        state = "IN_TREND"

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
# CORE ENGINE (SAFE)
# -----------------------------
def score_stock(ticker):

    try:
        if yf is None:
            return None

        df = yf.Ticker(ticker).history(period="3mo")

        if df is None or df.empty or len(df) < 30:
            return None

        if "Close" not in df or "Volume" not in df:
            return None

        close = df["Close"].values
        volume = df["Volume"].values
        price = float(df["Close"].iloc[-1])

        r = rsi(close)
        v = volume_intensity(volume)
        m = momentum(close)
        t = trend_strength(close)
        br = breakout(close)

        trend_bias = (m * 1.2) + (t * 1.0)

        if r > 65:
            trend_bias -= 0.5
        if r < 35:
            trend_bias += 0.5

        if trend_bias > 0.15:
            direction = "BULLISH"
        elif trend_bias < -0.15:
            direction = "BEARISH"
        else:
            direction = "NEUTRAL"

        bull = 0.5
        bear = 0.5

        if br:
            if direction == "BULLISH":
                bull += 0.15
            elif direction == "BEARISH":
                bear += 0.15

        bull += max(0, m * 0.4)
        bear += max(0, -m * 0.4)

        bull += max(0, t * 0.3)
        bear += max(0, -t * 0.3)

        if v > 1.3:
            if direction == "BULLISH":
                bull += 0.1
            elif direction == "BEARISH":
                bear += 0.1

        total = bull + bear
        bull /= total
        bear /= total

        confidence = abs(bull - bear)

        if direction == "BULLISH" and bull > 0.58:
            signal = "BULLISH"
        elif direction == "BEARISH" and bear > 0.58:
            signal = "BEARISH"
        else:
            signal = "NEUTRAL"

        setup = min(v * 0.3 + abs(m) + abs(t) + (1 if br else 0), 1.0)
        squeeze = min((v * 0.3 + (1 if br else 0) + abs(m) + abs(t)) / 3, 1.0)

        trade_plan = build_trade_plan(price, v, m, t, br)

        alerts = []

        if setup > 0.75 and confidence > 0.15:
            if direction == signal:
                alerts.append(f"EXTREME_{direction}")

        if setup > 0.60 and squeeze > 0.5:
            alerts.append("STRONG_SETUP")

        if trade_plan["state"] == "IN_TREND" and trade_plan["rr"] > 1.4:
            alerts.append("TREND_BREAKOUT_READY")

        score = (setup * 100 + squeeze * 60 + confidence * 80) / 3

        return {
            "ticker": ticker,
            "price": round(price, 2),
            "signal": signal,
            "direction": direction,
            "bull_prob": round(bull * 100, 1),
            "bear_prob": round(bear * 100, 1),
            "confidence": round(confidence * 100, 1),
            "squeeze_score": round(squeeze * 100, 1),
            "setup_score": round(setup * 100, 1),
            "score": round(score, 2),
            "alerts": alerts,
            "trade_plan": trade_plan
        }

    except Exception as e:
        print("[scanner error]", ticker, e)
        return None


def check_signal(ticker):
    return score_stock(ticker)
