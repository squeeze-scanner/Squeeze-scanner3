import requests
import time
import html

BOT_TOKEN = "8152536097:AAHyJsblgvVa5r2B12U-YeKt3-Z8O2dG_Kw"
CHAT_ID = "7376511550"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

_last_send_time = 0


def send_alert(message, retry=2):
    """
    Reliable Telegram sender:
    - rate limiting
    - retries
    - safe formatting
    """

    global _last_send_time

    if not message:
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

        # -----------------------------
        # SAFE MESSAGE
        # -----------------------------
        safe_msg = html.escape(str(message))[:3500]

        payload = {
            "chat_id": CHAT_ID,
            "text": safe_msg
        }

        # -----------------------------
        # RETRY LOGIC
        # -----------------------------
        for attempt in range(retry + 1):

            try:
                res = requests.post(BASE_URL, data=payload, timeout=6)

                print("[TELEGRAM DEBUG]", res.status_code, res.text)

                # success check
                if res.status_code == 200:
                    try:
                        data = res.json()
                        return bool(data.get("ok"))
                    except:
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
