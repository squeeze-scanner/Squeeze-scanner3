import requests
import time

# -----------------------------
# TELEGRAM CONFIG (FAKE TEST ID)
# -----------------------------
BOT_TOKEN = "8152536097:AAHyJsblgvVa5r2B12U-YeKt3-Z8O2dG_Kw"
CHAT_ID = "7376511550"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

_last_send_time = 0


# -----------------------------
# SAFE TELEGRAM SENDER (V2 STABLE)
# -----------------------------
def send_alert(message, retry=2):
    """
    Reliable Telegram sender with:
    - rate limiting
    - retries
    - full debug output
    """

    global _last_send_time

    if not message:
        print("[TELEGRAM] Empty message blocked")
        return False

    try:
        # -----------------------------
        # RATE LIMIT (1 msg/sec safe)
        # -----------------------------
        now = time.time()
        elapsed = now - _last_send_time

        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)

        _last_send_time = time.time()

        payload = {
            "chat_id": CHAT_ID,
            "text": str(message)[:3500]
        }

        # -----------------------------
        # RETRY LOOP
        # -----------------------------
        for attempt in range(retry + 1):

            try:
                res = requests.post(BASE_URL, data=payload, timeout=8)

                print("\n[TELEGRAM DEBUG]")
                print("STATUS:", res.status_code)
                print("RESPONSE:", res.text)

                try:
                    data = res.json()
                except Exception:
                    data = None

                # -----------------------------
                # HARD FAILURE CHECK
                # -----------------------------
                if res.status_code != 200:
                    print("[TELEGRAM FAIL] HTTP ERROR")
                    continue

                if data and data.get("ok") is True:
                    print("[TELEGRAM] SENT SUCCESSFULLY")
                    return True

                if data:
                    print("[TELEGRAM ERROR]", data.get("description"))

            except requests.exceptions.Timeout:
                print(f"[TELEGRAM TIMEOUT] attempt {attempt + 1}")

            except Exception as e:
                print(f"[TELEGRAM ERROR] attempt {attempt + 1}:", e)

            time.sleep(1.5 * (attempt + 1))

        print("[TELEGRAM] FAILED AFTER RETRIES")
        return False

    except Exception as e:
        print("[TELEGRAM FATAL ERROR]:", e)
        return False


# -----------------------------
# OPTIONAL MESSAGE BUILDER (USED BY APP)
# -----------------------------
def build_message(ticker, data, trade, alert_type="ENTRY"):
    price = data.get("price", 0)
    signal = data.get("signal", "NEUTRAL")
    setup = data.get("setup_score", 0)
    squeeze = data.get("squeeze_score", 0)
    bull = data.get("bull_prob", 0)
    bear = data.get("bear_prob", 0)

    entry = trade.get("entry", (0, 0))
    stop
