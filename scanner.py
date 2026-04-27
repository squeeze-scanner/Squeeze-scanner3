import numpy as np
import yfinance as yf


# -----------------------------
# UTIL
# -----------------------------
def arr(x):
    return np.array(x).reshape(-1)


# -----------------------------
# INDICATORS
# -----------------------------
def rsi(close):
    c = arr(close)

    if len(c) < 50:
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

    if len(v) < 30:
        return 1.0

    return v[-1] / (np.mean(v[-20:]) + 1e-9)


def momentum(close):
    c = arr(close)

    if len(c) < 30:
        return 0.0

    return (c[-1] / c[-10]) - 1


def trend_strength(close):
    c = arr(close)

    if len(c) < 50:
        return 0.0

    return (np.mean(c[-10:]) / (np.mean(c[-30:]) + 1e-9)) - 1


def breakout(close):
    c = arr(close)

    if len(c) < 30:
        return False

    return c[-1] > np.max(c[-25:-1])


# -----------------------------
# TRADE ENGINE (FIXED V4 CORE)
# -----------------------------
def build_trade_plan(price, v, m, t, br):

    volatility = max(abs(m) + abs(t), 0.02)

    # 🔥 REALISTIC ENTRY ZONE (NOT 0-0)
    atr_buffer = price * 0.008  # 0.8% zone

    entry_low = price - atr_buffer
    entry_high = price + atr_buffer

    # STOP based on volatility
    stop = price - (price * (0.02 + volatility * 0.4))

    risk = max(price - stop, price * 0.01)

    target1 = price + (risk * 1.5)
    target2 = price + (risk * 2.8)

    rr = (target1 - price) / risk

    # -----------------------------
    # STATE MACHINE (FIXED LOGIC)
    # -----------------------------
    if price < entry_low:
        state = "WAITING"
    elif entry_low <= price <= entry_high:
        state = "AT_ENTRY"
    else:
        state = "IN_TREND"

    # -----------------------------
    # SETUP TYPE
    # -----------------------------
    if br and v > 1.5:
        setup_type = "BREAKOUT_SQUEEZE"
    elif m > 0.04:
        setup_type = "MOMENTUM"
    elif t > 0.03:
        setup_type = "TREND"
    else:
        setup_type = "REVERSAL"

    return {
        "entry": (round(entry_low, 2), round(entry_high, 2)),
        "stop": round(stop, 2),
        "target1": round(target1, 2),
        "target2": round(target2, 2),
        "rr": round(rr, 2),
        "type": setup_type,
        "state": state
    }


# -----------------------------
# CORE ENGINE
# -----------------------------
def score_stock(ticker):

    try:
        df = yf.Ticker(ticker).history(period="6mo")

        if df is None or df.empty or len(df) < 60:
            return None

        if "Volume" not in df.columns:
            return None

        close = df["Close"].values
        volume = df["Volume"].values
        price = float(df["Close"].iloc[-1])

        # -----------------------------
        # INDICATORS
        # -----------------------------
        r = rsi(close)
        v = volume_intensity(volume)
        m = momentum(close)
        t = trend_strength(close)
        br = breakout(close)

        # -----------------------------
        # BULL / BEAR MODEL (FIXED)
        # -----------------------------
        bull = 0.5
        bear = 0.5

        if r < 40:
            bull += 0.2
        elif r > 65:
            bear += 0.2

        bull += max(0, m * 0.6)
        bear += max(0, -m * 0.6)

        bull += max(0, t * 0.5)
        bear += max(0, -t * 0.5)

        if v > 1.4:
            bull += 0.15

        if br:
            bull += 0.2

        total = bull + bear
        bull /= total
        bear /= total

        confidence = abs(bull - bear)

        # -----------------------------
        # SIGNAL
        # -----------------------------
        if bull > 0.65:
            signal = "BULLISH"
        elif bear > 0.65:
            signal = "BEARISH"
        else:
            signal = "NEUTRAL"

        # -----------------------------
        # SCORES (STABILIZED)
        # -----------------------------
        setup = min(v * 0.25 + abs(m) + abs(t) + (1 if br else 0), 1.0)

        squeeze = min((v * 0.3 + abs(m) + abs(t)) / 3, 1.0)

        # -----------------------------
        # TRADE PLAN (FIXED OUTPUT)
        # -----------------------------
        trade_plan = build_trade_plan(price, v, m, t, br)

        # -----------------------------
        # ALERTS
        # -----------------------------
        alerts = []

        if setup > 0.80 and confidence > 0.2:
            alerts.append("EXTREME_SETUP")

        if setup > 0.65 and squeeze > 0.55:
            alerts.append("STRONG_SETUP")

        if trade_plan["state"] == "IN_TREND" and trade_plan["rr"] > 1.5:
            alerts.append("TREND_BREAKOUT_READY")

        # -----------------------------
        # FINAL SCORE
        # -----------------------------
        score = (setup * 100 + squeeze * 70 + confidence * 90) / 3

        return {
            "ticker": ticker,
            "price": price,

            "signal": signal,

            "bull_prob": round(bull * 100, 1),
            "bear_prob": round(bear * 100, 1),
            "confidence": round(confidence * 100, 1),

            "setup_score": round(setup * 100, 1),
            "squeeze_score": round(squeeze * 100, 1),

            "score": round(score, 2),

            "alerts": alerts,

            # IMPORTANT (matches app.py)
            "trade_plan": trade_plan
        }

    except Exception as e:
        print(f"[scanner error {ticker}]: {e}")
        return None


def check_signal(ticker):
    return score_stock(ticker)
