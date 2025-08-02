import logging
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.database import engine
from app import models
from app.routers import (
    auth   as auth_router,
    jobs   as jobs_router,
    user   as user_router,
    admin  as admin_router,
)
from app.templating import templates
from app.core.config import settings
from app.core.logger import setup_logging

# راه‌اندازی لاگ‌گیری
setup_logging()
logger = logging.getLogger(__name__)

# بارگذاری تنظیمات محیطی
load_dotenv()

# تنظیم مسیرها
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / settings.STATIC_DIR
UPLOADS_DIR = BASE_DIR / settings.UPLOADS_DIR


# ایجاد جداول پایگاه‌داده
models.Base.metadata.create_all(bind=engine)

# تعریف دسته‌های مستندات OpenAPI
api_tags_metadata = [
    {
        "name": "🔐 احراز هویت",
        "description": "ورود، خروج و مدیریت توکن کاربران.",
    },
    {
        "name": "📥 فایل‌ها",
        "description": "آپلود، پیاده‌سازی و اصلاح فایل‌های صوتی یا متنی.",
    },
    {
        "name": "👤 کاربران",
        "description": "مشاهده، ایجاد و ویرایش اطلاعات کاربران توسط ادمین.",
    },
    {
        "name": "💰 کیف پول",
        "description": "مشاهده و مدیریت تراکنش‌های مالی کاربران.",
    },
    {
        "name": "⚙️ تنظیمات محتوا",
        "description": "مدیریت محتوای صفحات درباره ما، قوانین، پرسش‌ها و تعرفه‌ها.",
    },
]

# ایجاد برنامه اصلی FastAPI
app = FastAPI(
    title="دستیار صوت و متن",
    description="پیاده‌سازی و اصلاح صوت/متن با FastAPI",
    version="5.2.1",
    docs_url="/swagger",
    redoc_url=None,
    openapi_tags=api_tags_metadata
)

# اتصال پوشه‌های استاتیک و فایل‌های آپلود
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

@app.on_event("startup")
async def startup_event():
    """عملیات راه‌اندازی برنامه"""
    logger.info("Application starting up...")
    # ایجاد دایرکتوری‌های مورد نیاز
    for d in [UPLOADS_DIR, STATIC_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    logger.info("Application startup completed")

# ------------------- روت‌های عمومی -------------------
@app.get("/", response_class=HTMLResponse, tags=["🔐 احراز هویت"])
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "user": None})

@app.get("/terms", response_class=HTMLResponse, tags=["⚙️ تنظیمات محتوا"])
def terms_page(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request})

@app.get("/about", response_class=HTMLResponse, tags=["⚙️ تنظیمات محتوا"])
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/faq", response_class=HTMLResponse, tags=["⚙️ تنظیمات محتوا"])
def faq_page(request: Request):
    return templates.TemplateResponse("faq.html", {"request": request})

@app.get("/pricing", response_class=HTMLResponse, tags=["⚙️ تنظیمات محتوا"])
def pricing_page(request: Request):
    return templates.TemplateResponse("pricing.html", {"request": request})

@app.get("/change-password", response_class=HTMLResponse, tags=["🔐 احراز هویت"])
async def change_password_page(request: Request):
    return templates.TemplateResponse("change_password.html", {"request": request})

@app.get("/api-docs", response_class=HTMLResponse)
def api_docs_page(request: Request):
    return templates.TemplateResponse("api_docs.html", {"request": request})

# ------------------- اتصال روت‌های داخلی -------------------
app.include_router(auth_router.router, tags=["🔐 احراز هویت"])
app.include_router(jobs_router.router, tags=["📥 فایل‌ها"])
app.include_router(user_router.router, tags=["👤 کاربران"])
app.include_router(admin_router.router, tags=["👤 کاربران", "💰 کیف پول", "⚙️ تنظیمات محتوا"])