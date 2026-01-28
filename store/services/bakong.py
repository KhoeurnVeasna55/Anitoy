import requests
from django.conf import settings

def check_transaction_by_md5(md5: str) -> dict:

    url = f"{settings.BAKONG_BASE_URL}/v1/check_transaction_by_md5"

    headers = {
        "Authorization": f"Bearer {settings.BAKONG_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"md5": md5}

    r = requests.post(url, json=payload, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()
