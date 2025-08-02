from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# تنظیمات رمزنگاری
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    بررسی تطابق رمز عبور ساده با نسخه هش شده
    
    Args:
        plain_password: رمز عبور ورودی کاربر
        hashed_password: رمز هش شده در دیتابیس
    
    Returns:
        bool: True اگر رمزها مطابقت داشته باشند
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    تولید هش رمز عبور
    
    Args:
        password: رمز عبور خام
    
    Returns:
        str: رمز عبور هش شده
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    ایجاد توکن دسترسی JWT
    
    Args:
        data: داده‌های مورد نظر برای قرارگیری در توکن
        expires_delta: مدت زمان انقضای توکن
    
    Returns:
        str: توکن دسترسی رمزنگاری شده
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM
    )

def decode_token(token: str) -> dict:
    """
    رمزگشایی توکن JWT
    
    Args:
        token: توکن دریافتی
    
    Returns:
        dict: داده‌های داخل توکن
        
    Raises:
        JWTError: اگر توکن نامعتبر باشد
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise e