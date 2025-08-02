# app/celery_tasks.py

from app.celery_app import celery_app
from time import sleep
from typing import Dict, Any

@celery_app.task(name="parallel_audio_job")
def parallel_audio_job(record_id: int, file_path: str, language: str = "fa-IR") -> Dict[str, Any]:
    """
    یک تسک ساده برای تست پردازش موازی فایل صوتی.
    در پروژه واقعی می‌توان این تابع را با logic اصلی جایگزین کرد.
    """
    print(f"[🎧] Starting parallel audio job - Record ID: {record_id}, File: {file_path}, Lang: {language}")
    sleep(5)  # شبیه‌سازی پردازش
    print(f"[✅] Completed audio job for record {record_id}")
    
    return {
        "status": "completed",
        "record_id": record_id,
        "file_path": file_path,
        "language": language
    }
