from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from ..config import JWT_SECRET, JWT_ALGORITHM

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

def create_token(data: dict):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(days = 7)

    return jwt.encode(to_encode, JWT_SECRET, algorithm = JWT_ALGORITHM)
