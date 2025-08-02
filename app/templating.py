# app/templating.py
# ساخت و پیکربندی شیء Jinja2Templates مرکزی

from pathlib import Path
from fastapi.templating import Jinja2Templates
import jdatetime

BASE_DIR   = Path(__file__).resolve().parent.parent   # fastapi_transcriber/
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# اضافه کردن jdatetime به محیط Jinja2 تا در همهٔ قالب‌ها در دسترس باشد
templates.env.globals["jdatetime"] = jdatetime
