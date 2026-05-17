from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)
    
    @staticmethod
    def create_access_token(subject: str) -> str:
        payload = {
            "sub": subject,
            "exp": datetime.utcnow() + timedelta(minutes=15),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    
    @staticmethod
    def create_refresh_token(subject: str) -> str:
        payload = {
            "sub": subject,
            "exp": datetime.utcnow() + timedelta(days=7),
            "type": "refresh",
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    
    @staticmethod
    def verify_token(token: str) -> dict:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except JWTError:
            return None

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(subject: str) -> str:
    return AuthService.create_access_token(subject)

def create_refresh_token(subject: str) -> str:
    return AuthService.create_refresh_token(subject)
