# app/tasks/parallel_audio.py
# پردازش یک فایل صوتی به‌صورت ترتیبی، اما با قطعات موازی

import os
from pathlib import Path
from celery import group, chord
from sqlalchemy.orm import Session
from app.celery_app import celery_app
from app.database import SessionLocal
from app import models, crud
from app.services.audio_processing import AudioProcessor

# بقیه کدها بدون تغییر
from .helpers import to_clean_string

# 🔹 تسک برای پیاده‌سازی یک قطعه از صوت
@celery_app.task(name="transcribe_chunk")
def transcribe_chunk(part_path: str, start_sec: int, end_sec: int, lang: str) -> dict:
    import speech_recognition as sr

    recognizer = sr.Recognizer()
    with sr.AudioFile(part_path) as src:
        audio_data = recognizer.record(src)

    transcript = ""
    for attempt in range(5):
        try:
            transcript = recognizer.recognize_google(audio_data, language=lang)
            break
        except sr.UnknownValueError:
            break
        except sr.RequestError:
            if attempt < 4:
                import time
                time.sleep(1 + attempt)
                continue
            transcript = ""

    if not transcript.strip():
        transcript = f"({AudioProcessor.sec_to_mmss(start_sec)}-{AudioProcessor.sec_to_mmss(end_sec)})"

    return {"start": start_sec, "end": end_sec, "text": transcript}

# 🔹 مرحله نهایی بعد از همه chunkها
@celery_app.task(name="finalize_chunks")
def finalize_chunks(chunks_result: list[dict], record_id: int):
    db: Session = SessionLocal()
    try:
        final_text = "\n".join(to_clean_string(r["text"]) for r in sorted(chunks_result, key=lambda x: x["start"]))
        record = db.query(models.TranscriptionFile).get(record_id)
        if not record:
            raise ValueError("رکورد پیدا نشد")

        record.raw_result_text = final_text
        crud.transcriptions.finalize_job(db, record, final_text, 0)
    finally:
        db.commit()
        db.close()

# 🔹 وظیفه اصلی که فقط یک‌بار در لحظه اجرا می‌شود
@celery_app.task(bind=True, name="parallel_audio_job")
def parallel_audio_job(self, record_id: int, file_path: str, language: str):
    db: Session = SessionLocal()
    try:
        record = db.query(models.TranscriptionFile).get(record_id)
        if not record or record.status == "canceled":
            return

        crud.transcriptions.update_transcription_status(db, record_id, "processing")

        # تقسیم فایل به قطعات
        parts = AudioProcessor.split_audio(Path(file_path))
        tasks = []
        for idx, part in enumerate(parts):
            start = idx * 50
            end = start + 50
            tasks.append(transcribe_chunk.s(str(part), start, end, language))

        # اجرای موازی و سپس ذخیره نتیجه
        chord(group(tasks), finalize_chunks.s(record_id)).delay()

    finally:
        db.close()