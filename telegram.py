import requests
import time
import html

BOT_TOKEN = "8152536097:AAHyJsblgvVa5r2B12U-YeKt3-Z8O2dG_Kw"
CHAT_ID = "7376511550"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# -----------------------------
# RATE LIMIT STATE
# -----------------------------
_last_send_time = 0


def send_alert(message, retry=2):
    """
    Reliable Telegram sender:
    - rate limited
    - retries
    - debug output
    """

    global _last_send_time

    if not message:
        return False

    # -----------------------------
    # RATE LIMIT (1 msg/sec)
    # -----------------------------
    now = time.time()
    delay = now - _last_send_time

    if delay < 1.0:
        time.sleep(1.0 - delay)

    _last_send_time = time.time()

    # -----------------------------
    # SAFE MESSAGE
    # -----------------------------
    safe_msg = html.escape(str(message))[:3500]

    payload = {
        "chat_id": CHAT_ID,
        "text": safe_msg,
        "parse_mode": "HTML"
    }

    # -----------------------------
    # RETRY LOGIC
    # -----------------------------
    for attempt in range(retry + 1):

        try:
            res = requests.post(BASE_URL, data=payload, timeout=6)

            print("[TELEGRAM DEBUG]", res.status_code, res.text)

            # Telegram success check (IMPORTANT FIX)
            data = res.json()

            if data.get("ok") is True:
                return True

        except requests.exceptions.Timeout:
            print(f"[TELEGRAM TIMEOUT] attempt {attempt + 1}")

        except Exception as e:
            print(f"[TELEGRAM ERROR] attempt {attempt + 1}: {e}")

        time.sleep(1.5 * (attempt + 1))

    return False
