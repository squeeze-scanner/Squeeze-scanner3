import requests

BOT_TOKEN = "8152536097:AAHyJsblgvVa5r2B12U-YeKt3-Z8O2dG_Kw"
CHAT_ID = "7376511550"


def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram error:", e)
