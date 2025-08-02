import json, time, hmac, hashlib, requests


def post_with_signature(url: str, payload: dict, secret: str, timeout=10):
    """
    یک امضای ساده HMAC-SHA256 روی body می‌زند تا مشتری صحت پیام را تأیید کند.
    """
    body = json.dumps(payload, ensure_ascii=False).encode()
    signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-Signature": signature,
        "User-Agent": "fastapi-transcriber-webhook/1.0",
    }
    try:
        requests.post(url, data=body, headers=headers, timeout=timeout)
    except Exception as e:
        # فقط لاگ بکنید تا کار اصلی خراب نشود
        print(f"Webhook POST error ⇒ {e}")
