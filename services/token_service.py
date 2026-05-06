from utils.jwt_handler import create_access_token, create_refresh_token


def create_tokens(user_id):
    return {
        "access": create_access_token({"id": user_id}),
        "refresh": create_refresh_token({"id": user_id})
    }