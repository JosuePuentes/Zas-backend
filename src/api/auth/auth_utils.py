from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
import jwt

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2400 # 40 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    to_encode = {
        "id": str(user["_id"]),
        "name": user["rif"],
        "email": user["email"],
        "rif": user["rif"],
        "exp": datetime.utcnow() + expires_delta,
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_admin_access_token(admin: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    to_encode = {
        "id": str(admin["_id"]),
        "usuario": admin["usuario"],
        "rol": admin.get("rol", "admin"),
        "modulos": admin.get("modulos", []),
        "exp": datetime.utcnow() + expires_delta,
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
