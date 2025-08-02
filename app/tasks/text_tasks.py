# app/tasks/text_tasks.py
# وظایف Celery برای پردازش و اصلاح فایل‌های متنی
import os, time, concurrent.futures
from sqlalchemy.orm import Session
from pathlib import Path
from app.celery_app import celery_app
from app.database import SessionLocal
from app import models, crud
from app.services.text_processing import extract_text_from_docx, split_text_into_chunks
from .helpers import correct_single_text_chunk

@celery_app.task(bind=True, name="text_correct_task")
def background_text_correction_task(self, record_id: int, file_path: str):
    db: Session = SessionLocal()
    start_time = time.time()

    try:
        for _ in range(3):
            if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                break
            time.sleep(1)
        else:
            raise ValueError("فایل برای پردازش در دسترس نیست.")

        record = db.query(models.TranscriptionFile).get(record_id)
        if not record or record.status == "canceled":
            return

        user = record.owner
        crud.transcriptions.update_transcription_status(db, record_id, "processing")

        if file_path.endswith(".txt"):
            original_text = Path(file_path).read_text(encoding="utf-8")
        elif file_path.endswith(".docx"):
            original_text = extract_text_from_docx(file_path)
        else:
            raise ValueError("نوع فایل نامعتبر است.")

        chunks = list(split_text_into_chunks(original_text))
        tasks = [(i, c, user.token_price) for i, c in enumerate(chunks)]

        corrected = {}
        total_tokens = 0
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for idx, txt, used in executor.map(correct_single_text_chunk, tasks):
                if "[خطا" in txt:
                    raise ValueError(f"خطای AI در قطعه {idx}")
                corrected[idx] = txt
                total_tokens += used

        final_text = "\n".join(corrected[i] for i in sorted(corrected))

        crud.transactions.debit_from_wallet(
            db, user=user,
            cost=total_tokens * user.token_price,
            description=f"هزینه اصلاح فایل متنی: {record.original_filename}"
        )
        record.ai_token_usage = total_tokens

        crud.transcriptions.finalize_job(db, record, final_text, int(time.time() - start_time))

    except Exception as e:
        print(f"[Celery-Text] Record {record_id} failed: {e}")
        db.rollback()
        crud.transcriptions.update_transcription_status(db, record_id, "failed")
        raise
    finally:
        db.commit()
        db.close()
