# app/dependencies.py
# -*- coding: utf-8 -*-
"""
توابع کمکی/وابستگی‌های عمومی FastAPI
"""
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from . import crud, models, auth, database
from app.core.config import settings  # 🔧 اضافه شده

# برای API-های صرفاً JSON
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --------------------------------------------------
#  اتصال به دیتابیس (یک Session برای هر درخواست)
# --------------------------------------------------
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------------------------------
#  استخراج کاربر از «کوکی» (برای صفحات وب)
# --------------------------------------------------
async def get_current_user_from_cookie(
    request: Request,
    db: Session = Depends(get_db),
):
    token_cookie: str | None = request.cookies.get("access_token")

    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )

    if not token_cookie:
        raise cred_exc

    try:
        token_value = token_cookie.split(" ")[1]
        payload = jwt.decode(
            token_value,
            settings.SECRET_KEY.get_secret_value(),  # ✅ اصلاح‌شده
            algorithms=[settings.JWT_ALGORITHM]      # ✅ اصلاح‌شده
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise cred_exc
    except (JWTError, IndexError):
        raise cred_exc

    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise cred_exc
    return user

# --------------------------------------------------
#  استخراج کاربر از «هدر Authorization» (برای API)
# --------------------------------------------------
async def get_current_user_from_header(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),  # ✅ اصلاح‌شده
            algorithms=[settings.JWT_ALGORITHM]      # ✅ اصلاح‌شده
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise cred_exc
    except JWTError:
        raise cred_exc

    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise cred_exc
    return user

# --------------------------------------------------
#  بازرسی نقش‌ها
# --------------------------------------------------
async def get_current_admin(
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role != models.Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

async def get_current_employee_or_admin(
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role not in (models.Role.employee, models.Role.ADMIN):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

# --------------------------------------------------
#  بررسی مدیر فعال (سازگاری با نام قدیمی)
# --------------------------------------------------
async def get_current_active_admin(
    current_user: models.User = Depends(get_current_admin),
):
    return current_user
