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




    try:
        # -----------------------------
        # RATE LIMIT (anti spam + API protection)
        # -----------------------------
        now = time.time()
        delay = now - _last_send_time
def send_alert(message, retry=2):

    global _last_send_time

    if not message:
        return False

    now = time.time()
    delay = now - _last_send_time

    if delay < 1.0:
        time.sleep(1.0 - delay)

    _last_send_time = time.time()

    safe_msg = html.escape(str(message))[:3500]

    payload = {
        "chat_id": CHAT_ID,
        "text": safe_msg,
        "parse_mode": "HTML"
    }

    for attempt in range(retry + 1):

        try:
            res = requests.post(BASE_URL, data=payload, timeout=6)

            print("[TELEGRAM DEBUG]", res.status_code, res.text)

            data = res.json()

            if data.get("ok") is True:
                return True

        except Exception as e:
            print("[TELEGRAM ERROR]", e)

        time.sleep(1.5 * (attempt + 1))

    return False
        if delay < 1.0:
            time.sleep(1.0 - delay)

        _last_send_time = time.time()

        # -----------------------------
        # SAFE FORMAT (Telegram HTML safe)
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

                if res.status_code == 200:
                    return True

                print(f"[Telegram Error] attempt {attempt+1}: {res.text}")

            except requests.exceptions.Timeout:
                print(f"[Telegram Timeout] attempt {attempt+1}")

            except Exception as e:
                print(f"[Telegram Exception] attempt {attempt+1}: {e}")

            time.sleep(1.5 * (attempt + 1))

        return False

    except Exception as e:
        print("[Telegram Fatal Error]:", e)
        return False
