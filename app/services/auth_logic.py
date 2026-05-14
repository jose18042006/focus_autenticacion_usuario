import argon2
import jwt
import os
from datetime import datetime, timedelta, timezone

SECRET_KEY = os.getenv(
    "SECRET_KEY"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

_ph = argon2.PasswordHasher()

def hash_password(password: str) -> str:
    return _ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return _ph.verify(hashed_password, plain_password)
    except argon2.exceptions.VerifyMismatchError:
        return False
    except argon2.exceptions.InvalidHashError:
        return False

def create_access_token(email: str, user_id: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": email,          
        "user_id": str(user_id),
        "role": role,
        "exp": int(expire.timestamp()) 
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)