# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path
from datetime import date
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    File,
    Form,
    UploadFile,
)
from fastapi.responses import RedirectResponse, FileResponse
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename

from app.core.config import settings
from app.messages import (
    FILE_LIMIT_EXCEEDED,
    INVALID_FILE_TYPE,
    DAILY_LIMIT_EXCEEDED
)
from .. import dependencies, models
from ..dependencies import get_db
from ..crud import transcriptions, users
from ..tasks.text_tasks import background_text_correction_task
from ..tasks.parallel_audio import parallel_audio_job
from app.celery_app import celery_app

router = APIRouter(
    tags=["Jobs & Invoicing"],
    dependencies=[Depends(dependencies.get_current_user_from_cookie)],
)

# ──────────────────────────────────────────────────────────────────────────────
#                               AUDIO JOB
# ──────────────────────────────────────────────────────────────────────────────
@router.post("/transcribe/", summary="Create Audio Transcription Job")
async def create_audio_job(
    current_user: models.User = Depends(dependencies.get_current_user_from_cookie),
    db: Session = Depends(get_db),
    files: List[UploadFile] = File(...),
    language: str = Form(...),
    use_ai_correction: bool = Form(False),
):
    today = date.today()
    if current_user.last_transcription_date != today:
        current_user.daily_transcription_count = 0
        db.commit()
    db.refresh(current_user)

    if len(files) > (current_user.file_limit - current_user.daily_transcription_count):
        raise HTTPException(status_code=403, detail=FILE_LIMIT_EXCEEDED)

    for file in files:
        original_name = file.filename
        safe_name = secure_filename(original_name)
        stored_path = Path(settings.UPLOADS_DIR) / safe_name

        with stored_path.open("wb") as f:
            f.write(await file.read())

        prefix = settings.AI_PREFIX if use_ai_correction else settings.RAW_PREFIX
        display = f"{prefix} {original_name}"

        rec = transcriptions.create_transcription_record(
            db,
            filename=display,
            user_id=current_user.id,
            lang=language,
            original_filename=original_name,
        )

        async_res = parallel_audio_job.delay(rec.id, str(stored_path), language)
        transcriptions.set_task_id(db, rec.id, async_res.id)

        current_user.daily_transcription_count += 1
        current_user.last_transcription_date = today
        db.commit()

    return RedirectResponse("/dashboard?msg=transcribe-queued", status_code=303)

# ──────────────────────────────────────────────────────────────────────────────
#                               TEXT JOB
# ──────────────────────────────────────────────────────────────────────────────
@router.post("/correct-text/", summary="Create Text Correction Job")
async def create_text_job(
    current_user: models.User = Depends(dependencies.get_current_user_from_cookie),
    db: Session = Depends(get_db),
    files: List[UploadFile] = File(...),
):
    today = date.today()
    if current_user.last_transcription_date != today:
        current_user.daily_transcription_count = 0
        db.commit()
    db.refresh(current_user)

    if len(files) > (current_user.file_limit - current_user.daily_transcription_count):
        raise HTTPException(status_code=403, detail=DAILY_LIMIT_EXCEEDED)

    for file in files:
        if not file.filename.endswith((".txt", ".docx")):
            raise HTTPException(status_code=400, detail=INVALID_FILE_TYPE)

        original_name = file.filename
        stored_path = Path(settings.UPLOADS_DIR) / secure_filename(original_name)
        with stored_path.open("wb") as f:
            f.write(await file.read())

        rec = transcriptions.create_transcription_record(
            db,
            filename=f"(اصلاح متنی) {original_name}",
            user_id=current_user.id,
            lang="text",
            original_filename=original_name,
        )

        async_res = background_text_correction_task.delay(rec.id, str(stored_path))
        transcriptions.set_task_id(db, rec.id, async_res.id)

        current_user.daily_transcription_count += 1
        current_user.last_transcription_date = today
        db.commit()

    return RedirectResponse("/dashboard?msg=transcribe-canceled", status_code=303)

# ──────────────────────────────────────────────────────────────────────────────
#                               CANCEL JOB
# ──────────────────────────────────────────────────────────────────────────────
@router.post("/transcribe/{job_id}/cancel", summary="Cancel queued / running job")
def cancel_job(
    job_id: int,
    current_user: models.User = Depends(dependencies.get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    rec = transcriptions.get_job(db, job_id, current_user)
    if not rec:
        raise HTTPException(404, "Job not found")

    if rec.status in ("completed", "failed", "canceled"):
        raise HTTPException(400, "Job cannot be canceled")

    if rec.celery_task_id:
        task_id = rec.celery_task_id
        celery_app.control.revoke(task_id, terminate=True, signal='SIGTERM')

    transcriptions.update_transcription_status(db, job_id, "canceled")

    return RedirectResponse("/my-dashboard?msg=transcribe-canceled", status_code=303)

# ──────────────────────────────────────────────────────────────────────────────
#                               DOWNLOAD
# ──────────────────────────────────────────────────────────────────────────────
@router.get("/download/{record_id}/{file_type}", response_class=FileResponse, summary="Secure download")
def secure_download(
    record_id: int,
    file_type: str,
    current_user: models.User = Depends(dependencies.get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    rec = transcriptions.get_transcription(db, record_id)
    if not rec:
        raise HTTPException(404)

    if rec.user_id != current_user.id and current_user.role != models.Role.ADMIN:
        raise HTTPException(403)

    if file_type == "txt":
        fname = rec.output_filename_txt
    elif file_type == "docx":
        fname = rec.output_filename_docx
    else:
        raise HTTPException(400, "Invalid file type")

    if not fname:
        raise HTTPException(404, "فایل خروجی ثبت نشده")

    fpath = Path(settings.UPLOADS_DIR) / fname
    if not fpath.exists():
        raise HTTPException(404, "فایل یافت نشد")

    return FileResponse(
        str(fpath),
        filename=fname,
        media_type="application/octet-stream"
    )
