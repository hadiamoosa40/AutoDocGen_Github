from cryptography.fernet import Fernet
from config import ENCRYPTION_KEY

fernet = Fernet(ENCRYPTION_KEY)


def encrypt(data: str):
    return fernet.encrypt(data.encode()).decode()


def decrypt(data: str):
    return fernet.decrypt(data.encode()).decode()