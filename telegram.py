import requests
import time
import html

# ⚠️ your existing values kept as-is
BOT_TOKEN = "8152536097:AAHyJsblgvVa5r2B12U-YeKt3-Z8O2dG_Kw"
CHAT_ID = "7376511550"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# -----------------------------
# RATE LIMIT STATE
# -----------------------------
_last_send_time = 0


def send_alert(message, retry=2):
    """
    Sends a Telegram message safely with:
    - rate limiting
    - retries
    - HTML escaping
    """

    global _last_send_time

    if not message:
        return False

    try:
        # -----------------------------
        # RATE LIMIT (1 msg/sec)
        # -----------------------------
        now = time.time()
        delay = now - _last_send_time

        if delay < 1.0:
            time.sleep(1.0 - delay)

        _last_send_time = time.time()

        # -----------------------------
        # SAFE MESSAGE FORMAT
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

                if res.status_code == 200:
                    data = res.json()
                    if data.get("ok"):
                        return True

            except requests.exceptions.Timeout:
                print(f"[TELEGRAM TIMEOUT] attempt {attempt + 1}")

            except Exception as e:
                print(f"[TELEGRAM ERROR] attempt {attempt + 1}:", e)

            time.sleep(1.5 * (attempt + 1))

        return False

    except Exception as e:
        print("[TELEGRAM FATAL ERROR]:", e)
        return False
