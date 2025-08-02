# create_admin.py

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, crud, auth

def create_admin():
    db: Session = SessionLocal()

    username = "admin2"
    password = "admin123"

    existing_user = crud.get_user_by_username(db, username=username)
    if existing_user:
        print(f"✅ کاربر '{username}' قبلاً وجود دارد.")
        return

    hashed_password = auth.get_password_hash(password)

    new_user = models.User(
        username=username,
        hashed_password=hashed_password,
        role=models.Role.ADMIN,  # ← اصلاح شده
        file_limit=10,
        wallet_balance=0.0,
        token_price=10.0,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print(f"✅ کاربر مدیر '{username}' با موفقیت ایجاد شد.")

if __name__ == "__main__":
    create_admin()
