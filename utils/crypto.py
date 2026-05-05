import hmac
import hashlib

def verify_signature(secret: str, payload: bytes, signature: str):
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature)