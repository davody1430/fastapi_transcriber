# -*- coding: utf-8 -*-
"""
CRUD helpers for DastYar‑e SOT
"""

from __future__ import annotations
import os
import uuid
import logging
from datetime import date, datetime, timezone, timedelta
from typing import List, Optional

import docx
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import models, auth
from app.core.config import settings
from app.core.file_manager import file_manager

logger = logging.getLogger(__name__)

# =============================================================================
# 🕒 Helper
# =============================================================================
def _now_tehran() -> datetime:
    return datetime.now(timezone(timedelta(hours=3, minutes=30)))

# =============================================================================
# 🟢 کاربران
# =============================================================================
def get_user(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(
    db: Session,
    username_filter: str | None = None,
    skip: int = 0,
    limit: int = 100,
):
    q = db.query(models.User)
    if username_filter:
        q = q.filter(models.User.username.contains(username_filter))
    return q.order_by(models.User.id.desc()).offset(skip).limit(limit).all()

def create_user(db: Session, user_create) -> models.User:
    hashed_pw = auth.get_password_hash(user_create.password)
    db_user = models.User(
        username=user_create.username,
        hashed_password=hashed_pw,
        role=user_create.role,
        file_limit=user_create.file_limit,
        wallet_balance=user_create.wallet_balance,
        token_price=user_create.token_price,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User created: {db_user.username}")
    return db_user

def update_user_password(db: Session, user: models.User, new_plain_pw: str):
    user.hashed_password = auth.get_password_hash(new_plain_pw)
    db.commit()
    logger.info(f"Password updated for user: {user.username}")

def update_user_details(
    db: Session,
    user_to_update: models.User,
    username: str,
    file_limit: int,
    token_price: float,
):
    user_to_update.username = username
    user_to_update.file_limit = file_limit
    user_to_update.token_price = token_price
    db.commit()
    db.refresh(user_to_update)
    logger.info(f"User details updated: {user_to_update.username}")

# =============================================================================
# 🟢 تراکنش و کیف پول
# =============================================================================
def create_transaction(
    db: Session,
    user_id: int,
    amount: float,
    description: str,
    token_price: Optional[float] = None,
):
    tx = models.Transaction(
        user_id=user_id,
        amount=amount,
        description=description,
        token_price_at_transaction=token_price,
        timestamp=_now_tehran(),
    )
    db.add(tx)
    logger.info(f"Transaction created for user {user_id}: {description}")
    return tx

def adjust_user_balance(db: Session, user: models.User, amount: float, description: str):
    if amount == 0:
        return
    user.wallet_balance += amount
    create_transaction(db, user.id, amount, description, user.token_price)
    db.commit()
    db.refresh(user)
    logger.info(f"Balance adjusted for {user.username}: {amount}")

def debit_from_wallet(db: Session, user: models.User, cost: float, description: str):
    db.refresh(user)
    if user.wallet_balance < cost:
        logger.warning(f"Insufficient balance for user {user.username}")
        raise ValueError("موجودی ناکافی برای این عملیات")
    user.wallet_balance -= cost
    create_transaction(db, user.id, -cost, description, user.token_price)
    db.commit()
    db.refresh(user)
    logger.info(f"Debited {cost} from {user.username}")

# =============================================================================
# 🟢 فایل‌های رونوشت
# =============================================================================
def create_transcription_record(
    db: Session,
    filename: str,
    user_id: int,
    lang: str,
    original_filename: Optional[str] = None,
) -> models.TranscriptionFile:
    rec = models.TranscriptionFile(
        user_id=user_id,
        original_filename=original_filename or filename,
        display_filename=filename,
        language=lang,
        status="queued",
        timestamp=_now_tehran(),
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    logger.info(f"Transcription record created: {rec.id}")
    return rec

def set_task_id(db: Session, record_id: int, task_id: str):
    rec = db.query(models.TranscriptionFile).get(record_id)
    if rec:
        rec.celery_task_id = task_id
        db.commit()
        logger.info(f"Task ID set for record {record_id}: {task_id}")

def update_transcription_status(db: Session, record_id: int, status: str):
    rec = db.query(models.TranscriptionFile).get(record_id)
    if rec:
        rec.status = status
        if status in ("completed", "failed", "canceled"):
            rec.finished_at = _now_tehran()
        db.commit()
        logger.info(f"Status updated for record {record_id}: {status}")

def finalize_job(
    db: Session,
    record: models.TranscriptionFile,
    final_text: str,
    duration: int,
):
    record.status = "completed"
    record.final_result_text = final_text
    record.processing_duration_seconds = duration

    base = f"{record.id}_{record.original_filename.rsplit('.', 1)[0]}"
    txt_name = f"{base}.txt"
    file_manager.save_file(final_text.encode('utf-8'), txt_name)
    record.output_filename_txt = txt_name

    doc = docx.Document()
    doc.add_paragraph(final_text)
    docx_name = f"{base}.docx"
    doc_path = file_manager.get_upload_path(docx_name)
    doc.save(doc_path)
    record.output_filename_docx = docx_name

    db.commit()
    logger.info(f"Job finalized: {record.id}")

def get_job(db: Session, job_id: int, owner: models.User):
    q = db.query(models.TranscriptionFile).filter_by(id=job_id)
    if owner.role != models.Role.admin:
        q = q.filter_by(user_id=owner.id)
    return q.first()

# =============================================================================
# 🟢 کوئری‌های رونوشت برای صفحات
# =============================================================================
def get_transcription(db: Session, record_id: int) -> models.TranscriptionFile | None:
    return db.query(models.TranscriptionFile).get(record_id)

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

def get_all_transcriptions(db: Session, skip: int = 0, limit: int = 15):
    return (
        db.query(models.TranscriptionFile)
        .order_by(models.TranscriptionFile.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_all_transcriptions_count(db: Session) -> int:
    return db.query(models.TranscriptionFile).count()

def get_transcriptions_by_ids(db: Session, user_id: int, job_ids: List[int]):
    return (
        db.query(models.TranscriptionFile)
        .filter(
            models.TranscriptionFile.id.in_(job_ids),
            models.TranscriptionFile.user_id == user_id,
        )
        .all()
    )

# =============================================================================
# 🟢 تراکنش‌ها (گزارش)
# =============================================================================
def get_user_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 15):
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.user_id == user_id)
        .order_by(models.Transaction.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_user_transactions_count(db: Session, user_id: int) -> int:
    return db.query(models.Transaction).filter(models.Transaction.user_id == user_id).count()

def get_all_transactions(
    db: Session,
    username_filter: str | None = None,
    skip: int = 0,
    limit: int = 15,
):
    q = db.query(models.Transaction).join(models.User)
    if username_filter:
        q = q.filter(models.User.username.contains(username_filter))
    return (
        q.order_by(models.Transaction.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_all_transactions_count(db: Session, username_filter: str | None = None) -> int:
    q = db.query(models.Transaction).join(models.User)
    if username_filter:
        q = q.filter(models.User.username.contains(username_filter))
    return q.count()

# =============================================================================
# 🟢 Settings
# =============================================================================
def get_setting(db: Session, key: str):
    return db.query(models.Setting).filter(models.Setting.key == key).first()

def update_setting(db: Session, key: str, value: str):
    s = get_setting(db, key)
    if s:
        s.value = value
    else:
        s = models.Setting(key=key, value=value)
        db.add(s)
    db.commit()
    logger.info(f"Setting updated: {key}")

def upsert_setting(db: Session, key: str, value: str):
    try:
        setting = db.query(models.Setting).filter(models.Setting.key == key).one()
        setting.value = value
    except NoResultFound:
        setting = models.Setting(key=key, value=value)
        db.add(setting)
    db.commit()
    db.refresh(setting)
    logger.info(f"Setting upserted: {key}")
    return setting

# =============================================================================
# 🟢 API KEY CRUD
# =============================================================================
def _generate_api_key() -> str:
    return uuid.uuid4().hex + uuid.uuid4().hex

def create_api_key(db: Session, user: models.User) -> models.APIKey:
    key = _generate_api_key()
    api_key = models.APIKey(key=key, owner=user)
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    logger.info(f"API key created for user: {user.username}")
    return api_key

def get_api_key(db: Session, key_str: str) -> Optional[models.APIKey]:
    return db.query(models.APIKey).filter(models.APIKey.key == key_str).first()

def get_api_key_by_user(db: Session, user: models.User) -> Optional[models.APIKey]:
    return (
        db.query(models.APIKey)
        .filter(models.APIKey.user_id == user.id, models.APIKey.is_active.is_(True))
        .first()
    )

def deactivate_api_key(db: Session, api_key: models.APIKey):
    api_key.is_active = False
    db.commit()
    logger.info(f"API key deactivated: {api_key.key}")