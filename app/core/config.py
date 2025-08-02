from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# تعریف کلاس تنظیمات کلی برنامه
class Settings(BaseSettings):
    # کلید API برای GapGPT و قیمت پیش‌فرض توکن
    GAPGPT_API_KEY: SecretStr
    DEFAULT_TOKEN_PRICE: float = 10.0

    # تنظیمات مربوط به Celery و Redis
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # کلید رمز برای امضای توکن‌های JWT
    SECRET_KEY: SecretStr

    # زمان انقضای توکن دسترسی بر حسب دقیقه
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # الگوریتم رمزنگاری JWT
    JWT_ALGORITHM: str = "HS256"

    # پیشوندهای مختلف برای نام‌گذاری فایل‌ها در پردازش‌ها
    AI_PREFIX: str = "(AI)"
    RAW_PREFIX: str = "(RAW)"
    TEXT_PREFIX: str = "(اصلاح متنی)"

    # حداکثر دفعات تلاش مجدد برای پردازش‌های مختلف
    AI_MAX_RETRIES: int = 3
    AUDIO_MAX_RETRIES: int = 3

    # مسیر دایرکتوری‌های پروژه برای فایل‌های ایستا، قالب‌ها و آپلودها
    STATIC_DIR: str = "static"
    TEMPLATES_DIR: str = "templates"
    UPLOADS_DIR: str = "uploads"

    # تنظیمات پایه برای بارگذاری فایل .env و محدود کردن مقادیر اضافی
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid"
    )

# ایجاد شیء تنظیمات که در سایر بخش‌های پروژه استفاده خواهد شد
settings = Settings()
