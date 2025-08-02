# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- بازگشت به استفاده از دیتابیس محلی SQLite ---
# این آدرس به برنامه می‌گوید که یک فایل به نام transcriber.db در ریشه پروژه ایجاد کند.
SQLALCHEMY_DATABASE_URL = "sqlite:///./transcriber.db"

# ساخت موتور SQLAlchemy برای اتصال به دیتابیس
# آرگومان connect_args برای سازگاری با SQLite ضروری است
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# ساخت یک کلاس Session برای ارتباط با دیتابیس در هر درخواست
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ساخت یک کلاس پایه برای تمام مدل‌های دیتابیس
Base = declarative_base()