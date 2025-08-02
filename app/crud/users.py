# app/crud/users.py
# مدیریت عملیات CRUD کاربران
from sqlalchemy.orm import Session
from app import models, auth, schemas

# دریافت یک کاربر با ID
def get_user(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()

# دریافت کاربر بر اساس username
def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()

# دریافت لیستی از کاربران با قابلیت جستجو و صفحه‌بندی
def get_users(db: Session, username_filter: str | None = None, skip: int = 0, limit: int = 100):
    q = db.query(models.User)
    if username_filter:
        q = q.filter(models.User.username.contains(username_filter))
    return q.order_by(models.User.id.desc()).offset(skip).limit(limit).all()

# ایجاد کاربر جدید
def create_user(db: Session, user_create: schemas.UserCreate) -> models.User:
    hashed_pw = auth.get_password_hash(user_create.password)
    db_user = models.User(
        username=user_create.username,
        hashed_password=hashed_pw,
        role=user_create.role,
        file_limit=user_create.file_limit,
        wallet_balance=user_create.wallet_balance,
        token_price=user_create.token_price,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# به‌روزرسانی رمز عبور کاربر
def update_user_password(db: Session, user: models.User, new_plain_pw: str):
    user.hashed_password = auth.get_password_hash(new_plain_pw)
    db.commit()

# به‌روزرسانی جزئیات کاربر
def update_user_details(db: Session, user_to_update: models.User, username: str, file_limit: int, token_price: float):
    user_to_update.username = username
    user_to_update.file_limit = file_limit
    user_to_update.token_price = token_price
    db.commit()
    db.refresh(user_to_update)
