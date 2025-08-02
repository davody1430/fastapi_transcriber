# app/celery_app.py

import os
from celery import Celery
from dotenv import load_dotenv
from app.core.config import settings



# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# راه‌اندازی برنامه Celery با استفاده از تنظیمات محیطی
celery_app = Celery(
    "dastyaresot",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.audio",
        "app.tasks.text_tasks",
        "app.tasks.external_tasks",
        "app.tasks.maintenance",       # برای Beat schedule
    ]
)

# تنظیمات عمومی Celery
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Tehran",
    enable_utc=True,
    task_default_queue="default",
    task_create_missing_queues=True,
    task_default_retry_delay=60,       # تأخیر پیش‌فرض برای تلاش مجدد (1 دقیقه)
    task_max_retries=3,
    task_track_started=True,
    result_expires=86400,              # انقضای نتایج: 24 ساعت
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    worker_max_tasks_per_child=100,
    worker_send_task_events=True,
    event_queue_expires=60,
    worker_proc_alive_timeout=30,
)

# تعیین مسیر صف برای هر تسک
celery_app.conf.task_routes = {
    "app.tasks.audio.*": {"queue": "audio"},
    "app.tasks.text_tasks.*": {"queue": "text"},
    "app.tasks.external_tasks.*": {"queue": "api"},
    "app.tasks.maintenance.*": {"queue": "maintenance"},
}

# تنظیمات خاص برای تسک‌ها
celery_app.conf.task_annotations = {
    "app.tasks.audio.parallel_audio_job": {
        "time_limit": 1800,
        "soft_time_limit": 1500,
        "max_retries": 5,
        "default_retry_delay": 120,
    },
    "app.tasks.text_tasks.background_text_correction_task": {
        "time_limit": 600,
        "max_retries": 3,
    },
    "app.tasks.external_tasks.enqueue_external_job": {
        "time_limit": 1200,
        "rate_limit": "10/m",
    },
}

# تعریف تسک‌های دوره‌ای (Beat schedule)
celery_app.conf.beat_schedule = {
    "cleanup_expired_sessions": {
        "task": "app.tasks.maintenance.cleanup_expired_sessions",
        "schedule": 3600,  # هر ساعت
        "options": {"queue": "maintenance"}
    },
    "update_daily_limits": {
        "task": "app.tasks.maintenance.reset_daily_limits",
        "schedule": 86400,  # روزانه
        "options": {"queue": "maintenance"}
    }
}

# اجرای مستقیم در صورت نیاز (برای CLI یا اجرای دستی)
if __name__ == "__main__":
    celery_app.start()
