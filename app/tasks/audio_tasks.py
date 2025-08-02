# app/tasks/audio_tasks.py
# وظایف Celery مربوط به پردازش فایل‌های صوتی
import time
from sqlalchemy.orm import Session
from app.celery_app import celery_app
from app.database import SessionLocal
from app import models, crud
from app.services.audio_processing import transcribe_audio_google
from .helpers import to_clean_string
from app.services.ai_services import correct_text_with_ai

@celery_app.task(bind=True, name="audio_transcribe_task")
def background_audio_task(self, record_id: int, file_path: str, language: str, process_ai: bool, original_filename: str):
    db: Session = SessionLocal()
    start_time = time.time()

    try:
        record = db.query(models.TranscriptionFile).get(record_id)
        if not record or record.status == "canceled":
            return

        user = record.owner
        if process_ai and user.wallet_balance < (200 * user.token_price):
            raise ValueError("موجودی برای اصلاح با هوش مصنوعی کافی نیست.")

        crud.transcriptions.update_transcription_status(db, record_id, "processing")

        raw_segments = transcribe_audio_google(file_path, language)
        raw_text_str = to_clean_string(raw_segments)
        if not raw_text_str or "[خطا" in raw_text_str:
            raise ValueError("پیاده‌سازی صوت ناموفق بود.")

        record.raw_result_text = raw_text_str
        final_text, token_usage = raw_text_str, 0

        if process_ai:
            corrected_text, token_usage = correct_text_with_ai(raw_text_str, user.token_price)
            if "[خطا" in corrected_text:
                raise ValueError("اصلاح با هوش مصنوعی ناموفق بود.")

            final_text = corrected_text
            record.ai_result_text = corrected_text
            record.ai_token_usage = token_usage

            crud.transactions.debit_from_wallet(
                db, user=user,
                cost=token_usage * user.token_price,
                description=f"هزینه اصلاح فایل: {original_filename}"
            )

        crud.transcriptions.finalize_job(db, record, final_text, int(time.time() - start_time))

    except Exception as e:
        print(f"[Celery-Audio] Record {record_id} failed: {e}")
        db.rollback()
        crud.transcriptions.update_transcription_status(db, record_id, "failed")
        raise
    finally:
        db.commit()
        db.close()
