import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.core.config import settings

def setup_logging():
    """پیکربندی سیستم لاگ‌گیری"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # فرمت پایه
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # هندلر کنسول
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # هندلر فایل (چرخشی)
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=1024 * 1024 * 5,  # 5 MB
        backupCount=3
    )
    file_handler.setFormatter(formatter)

    # سطح پایه لاگ‌گیری
    logging.basicConfig(
        level=logging.INFO,
        handlers=[console_handler, file_handler]
    )

    # لاگ‌های خاص
    sql_logger = logging.getLogger('sqlalchemy.engine')
    sql_logger.setLevel(logging.WARNING)

    # لاگ‌های سوم‌پارت‌ها
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('celery').setLevel(logging.INFO)