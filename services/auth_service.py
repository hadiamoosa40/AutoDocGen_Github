from utils.jwt_handler import create_access_token, create_refresh_token


def generate_tokens(user):
    payload = {"id": str(user["_id"])}
    return {
        "access": create_access_token(payload),
        "refresh": create_refresh_token(payload)
    }