import requests
import time
import html

BOT_TOKEN = "8152536097:AAHyJsblgvVa5r2B12U-YeKt3-Z8O2dG_Kw"
CHAT_ID = "7376511550"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# -----------------------------
# SIMPLE RATE LIMIT (PREVENT SPAM BLOCK)
# -----------------------------
_last_send_time = 0


def send_alert(message, retry=2):
    """
    Robust Telegram alert system:
    - rate limited
    - retries on failure
    - safe formatting
    """

    global _last_send_time

    if not message:
        return False

    # -----------------------------
    # RATE LIMIT (1 msg/sec safety)
    # -----------------------------
    now = time.time()
    if now - _last_send_time < 1:
        time.sleep(1)

    _last_send_time = time.time()

    # -----------------------------
    # SAFE MESSAGE HANDLING
    # -----------------------------
    safe_msg = html.escape(str(message))[:3500]

    payload = {
        "chat_id": CHAT_ID,
        "text": safe_msg,
        "parse_mode": "HTML"
    }

    # -----------------------------
    # SEND WITH RETRIES
    # -----------------------------
    for attempt in range(retry + 1):

        try:
            res = requests.post(BASE_URL, data=payload, timeout=5)

            if res.status_code == 200:
                return True

            print(f"Telegram error (attempt {attempt+1}):", res.text)

        except requests.exceptions.Timeout:
            print(f"Telegram timeout (attempt {attempt+1})")

        except Exception as e:
            print(f"Telegram error (attempt {attempt+1}):", e)

        time.sleep(1.5 * (attempt + 1))

    return False
