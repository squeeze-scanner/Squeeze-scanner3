import requests
import time
import html

# -----------------------------
# TELEGRAM CONFIG
# -----------------------------
BOT_TOKEN = "8152536097:AAHyJsblgvVa5r2B12U-YeKt3-Z8O2dG_Kw"
CHAT_ID = "7376511550"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

_last_send_time = 0


# -----------------------------
# SAFE SENDER (V2 STABLE ENGINE)
# -----------------------------
def send_alert(message, retry=2):
    global _last_send_time

    if not message:
        return False

    try:
        now = time.time()
        elapsed = now - _last_send_time

        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)

        _last_send_time = time.time()

        payload = {
            "chat_id": CHAT_ID,
            "text": str(message)[:3500]
        }

        for attempt in range(retry + 1):

            try:
                res = requests.post(BASE_URL, data=payload, timeout=6)

                print("[TELEGRAM STATUS]", res.status_code)
                print("[TELEGRAM RESPONSE]", res.text)

                data = None
                try:
                    data = res.json()
                except:
                    pass

                if res.status_code == 200 and data and data.get("ok"):
                    return True

                # 🔥 IMPORTANT: show real failure reason
                if data:
                    print("[TELEGRAM ERROR]", data.get("description"))

            except requests.exceptions.Timeout:
                print(f"[TELEGRAM TIMEOUT] attempt {attempt + 1}")

            except Exception as e:
                print(f"[TELEGRAM ERROR] attempt {attempt + 1}:", e)

            time.sleep(1.5 * (attempt + 1))

        return False

    except Exception as e:
        print("[TELEGRAM FATAL ERROR]:", e)
        return False


# -----------------------------
# V2 MESSAGE BUILDER (OPTIONAL BUT USED BY APP.PY)
# -----------------------------
def build_message(ticker, data, trade, alert_type="ENTRY"):
    price = data.get("price", 0)
    signal = data.get("signal", "NEUTRAL")
    setup = data.get("setup_score", 0)
    squeeze = data.get("squeeze_score", 0)
    bull = data.get("bull_prob", 0)
    bear = data.get("bear_prob", 0)

    entry = trade.get("entry", (0, 0))
    stop = trade.get("stop", 0)
    t1 = trade.get("target1", 0)
    t2 = trade.get("target2", 0)
    rr = trade.get("rr", 0)
    state = trade.get("state", "WAITING")
    setup_type = trade.get("type", "UNKNOWN")

    header = "🚀 V2 EXECUTION ALERT"

    if alert_type == "EXTREME":
        header = "🔥 EXTREME TRADE SETUP"
    elif alert_type == "BREAKOUT":
        header = "🚀 BREAKOUT CONFIRMED"
    elif alert_type == "ENTRY":
        header = "⚡ ENTRY ZONE ALERT"

    msg = f"""
{header}

{ticker} | {signal} | ${price}
STATE: {state}
TYPE: {setup_type}

ENTRY: {entry}
STOP: {stop}
TARGET 1: {t1}
TARGET 2: {t2}
RR: {rr}

SETUP: {setup}%
SQUEEZE: {squeeze}%
BULL: {bull}% | BEAR: {bear}%
"""

    return msg.strip()
