import secrets

def generate_secret():
    return secrets.token_urlsafe(32)