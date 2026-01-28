import requests
from django.conf import settings

def send_telegram_message(text: str) -> dict:
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    chat_id = getattr(settings, "TELEGRAM_CHAT_ID", "")

    if not token or not chat_id:
        return {"ok": False, "error": "Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID"}

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()
    return r.json()
