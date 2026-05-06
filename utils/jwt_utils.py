from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
import hashlib
import secrets

SECRET_KEY = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-this")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def hash_password(password: str) -> str:
    """Simple password hashing (fallback if bcrypt not available)"""
    salt = secrets.token_hex(16)
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest() + ":" + salt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Simple password verification"""
    try:
        hashed, salt = hashed_password.split(":")
        return hashed == hashlib.sha256(f"{plain_password}{salt}".encode()).hexdigest()
    except:
        return False