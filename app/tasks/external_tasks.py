# app/tasks/external_tasks.py
# پردازش وظایف از API خارجی
import requests, shutil
from pathlib import Path
from sqlalchemy.orm import Session
from app.celery_app import celery_app
from app.database import SessionLocal
from app import models
from .audio_tasks import background_audio_task

@celery_app.task(bind=True, name="external_job_task")
def enqueue_external_job(self, job_id: int, file_url: str, language: str, mode: str, callback_url: str | None = None):
    db: Session = SessionLocal()
    try:
        record = db.query(models.TranscriptionFile).get(job_id)
        if not record:
            raise ValueError("Job not found")

        local_path = Path("uploads") / f"ext_{job_id}_{Path(file_url).name}"
        with requests.get(file_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(local_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)

        background_audio_task.delay(job_id, str(local_path), language, mode != "transcribe_only", local_path.name)

        # ارسال به callback_url (اختیاری)
        # TODO: پیاده‌سازی webhook برای ارسال نتیجه

    except Exception as e:
        print(f"[Celery-External] Job {job_id} failed: {e}")
        raise
    finally:
        db.close()
