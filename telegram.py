import requests

BOT_TOKEN = "8152536097:AAHyJsblgvVa5r2B12U-YeKt3-Z8O2dG_Kw"
CHAT_ID = "7376511550"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def send_alert(message):
    """
    Sends Telegram alert safely with timeout + validation.
    """

    if not message:
        return False

    payload = {
        "chat_id": CHAT_ID,
        "text": str(message)[:3500],  # safety cap
        "parse_mode": "HTML"
    }

    try:
        res = requests.post(BASE_URL, data=payload, timeout=5)

        # confirm success
        if res.status_code == 200:
            return True
        else:
            print("Telegram error response:", res.text)
            return False

    except requests.exceptions.Timeout:
        print("Telegram timeout")
        return False

    except Exception as e:
        print("Telegram error:", e)
        return False
