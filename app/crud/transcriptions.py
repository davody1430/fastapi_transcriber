# app/crud/transcriptions.py
import os
import docx
from sqlalchemy.orm import Session
from app import models
from sqlalchemy.orm import Session
from app import models
from app.utils.time import now_tehran  # تغییر اینجا
from sqlalchemy.orm import Session
from .. import models
UPLOAD_DIR = "uploads"

def create_transcription_record(db: Session, filename: str, user_id: int, lang: str, original_filename: str | None = None):
    rec = models.TranscriptionFile(
        user_id=user_id,
        original_filename=original_filename or filename,
        display_filename=filename,
        language=lang,
        status="queued",
        timestamp=now_tehran(),  # تغییر اینجا
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def get_user_transcriptions(db: Session, user_id: int, skip: int = 0, limit: int = 15):
    return (
        db.query(models.TranscriptionFile)
        .filter(models.TranscriptionFile.user_id == user_id)
        .order_by(models.TranscriptionFile.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_user_transcriptions_count(db: Session, user_id: int) -> int:
    return db.query(models.TranscriptionFile).filter(models.TranscriptionFile.user_id == user_id).count()

def set_task_id(db: Session, record_id: int, task_id: str):
    rec = db.query(models.TranscriptionFile).get(record_id)
    if rec:
        rec.celery_task_id = task_id
        db.commit()

def update_transcription_status(db: Session, record_id: int, status: str):
    rec = db.query(models.TranscriptionFile).get(record_id)
    if rec:
        rec.status = status
        if status in ("completed", "failed", "canceled"):
            rec.finished_at = now_tehran()  # تغییر اینجا
        db.commit()

def finalize_job(db: Session, record: models.TranscriptionFile, final_text: str, duration: int):
    record.status = "completed"
    record.final_result_text = final_text
    record.processing_duration_seconds = duration

    base = f"{record.id}_{record.original_filename.rsplit('.', 1)[0]}"
    txt_name = f"{base}.txt"
    with open(os.path.join(UPLOAD_DIR, txt_name), "w", encoding="utf-8") as f:
        f.write(final_text)
    record.output_filename_txt = txt_name

    doc = docx.Document()
    doc.add_paragraph(final_text)
    docx_name = f"{base}.docx"
    doc.save(os.path.join(UPLOAD_DIR, docx_name))
    record.output_filename_docx = docx_name

    db.commit()


def get_all_transcriptions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transcription).order_by(models.Transcription.created_at.desc()).offset(skip).limit(limit).all()

def get_job(db: Session, job_id: int, owner: models.User):
    q = db.query(models.TranscriptionFile).filter_by(id=job_id)
    if owner.role != models.Role.ADMIN:
        q = q.filter_by(user_id=owner.id)
    return q.first()