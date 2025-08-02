import os
from dotenv import load_dotenv
from app.database import SessionLocal, engine
from app.models import Role, Base
from app.schemas import UserCreate
from app.crud import create_user, get_user_by_username

# خواندن متغیرهای محیطی برای پیدا کردن قیمت پیش‌فرض
load_dotenv()

def main():
    """
    تابع اصلی برای ساخت کاربر مدیر و تنظیمات اولیه.
    """
    print("Ensuring database tables are created...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    db = SessionLocal()
    try:
        ADMIN_USERNAME = "admin"
        ADMIN_PASSWORD = "admin" # لطفاً پس از اولین ورود این رمز را تغییر دهید

        print("Checking for existing admin user...")
        if get_user_by_username(db, ADMIN_USERNAME):
            print(f"User '{ADMIN_USERNAME}' already exists.")
            return

        print("Admin user not found. Creating...")
        
        # خواندن قیمت پیش‌فرض از فایل .env یا استفاده از مقدار ۱۰
        default_token_price = float(os.getenv("DEFAULT_TOKEN_PRICE", 10.0))
        
        admin_user = UserCreate(
            username=ADMIN_USERNAME,
            password=ADMIN_PASSWORD,
            role=Role.admin,
            file_limit=1000,
            wallet_balance=1000000.0,
            token_price=default_token_price
        )
        create_user(db, admin_user)
        print("✅ Admin user created successfully!")
        print(f"   - Username: {ADMIN_USERNAME}")
        print(f"   - Password: {ADMIN_PASSWORD}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
