import hashlib
import hmac
import os
import secrets
import string
from fastapi import HTTPException, Request, status

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "your-webhook-secret")

# In-memory state store (use Redis in true production)
_oauth_states: dict[str, bool] = {}


def generate_oauth_state(length: int = 32) -> str:
    """Generate a cryptographically secure random state string."""
    alphabet = string.ascii_letters + string.digits
    state = "".join(secrets.choice(alphabet) for _ in range(length))
    _oauth_states[state] = True
    return state


def verify_oauth_state(state: str) -> bool:
    """Verify and consume the state (one-time use)."""
    if state in _oauth_states:
        del _oauth_states[state]
        return True
    return False


def verify_github_webhook_signature(payload_body: bytes, signature_header: str | None) -> bool:
    """Verify GitHub webhook HMAC-SHA256 signature."""
    if not signature_header:
        return False
    if not signature_header.startswith("sha256="):
        return False

    expected = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        payload_body,
        hashlib.sha256,
    ).hexdigest()
    received = signature_header[len("sha256="):]

    return hmac.compare_digest(expected, received)


def generate_webhook_secret() -> str:
    return secrets.token_hex(32)