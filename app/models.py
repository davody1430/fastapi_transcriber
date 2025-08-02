# -*- coding: utf-8 -*-
from __future__ import annotations

import enum
from datetime import datetime, date

import jdatetime
import pytz
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from .database import Base


class Role(str, enum.Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"
    CUSTOMER = "customer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.CUSTOMER)

    created_at = Column(DateTime, default=datetime.utcnow)
    file_limit = Column(Integer, default=5)
    daily_transcription_count = Column(Integer, default=0)
    last_transcription_date = Column(Date, nullable=True)

    wallet_balance = Column(Float, default=0.0)
    token_price = Column(Float, default=10.0)
    is_active = Column(Boolean, default=True)

    transcriptions = relationship("TranscriptionFile", back_populates="owner")
    transactions = relationship("Transaction", back_populates="user")
    api_keys = relationship("APIKey", back_populates="owner")


class TranscriptionFile(Base):
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    original_filename = Column(String, nullable=False)
    display_filename = Column(String, nullable=False)
    language = Column(String, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending | queued | processing | completed | failed | canceled

    celery_task_id = Column(String(50), nullable=True, index=True)

    raw_result_text = Column(Text, nullable=True)
    ai_result_text = Column(Text, nullable=True)
    final_result_text = Column(Text, nullable=True)

    processing_duration_seconds = Column(Integer, nullable=True)
    ai_token_usage = Column(Integer, nullable=True)

    output_filename_txt = Column(String, nullable=True)
    output_filename_docx = Column(String, nullable=True)

    owner = relationship("User", back_populates="transcriptions")

    @hybrid_property
    def timestamp_local(self):
        utc_ts = self.timestamp.replace(tzinfo=pytz.utc)
        local_tz = pytz.timezone("Asia/Tehran")
        return utc_ts.astimezone(local_tz)

    @hybrid_property
    def user(self):
        return self.owner


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow)
    token_price_at_transaction = Column(Float, nullable=True)

    user = relationship("User", back_populates="transactions")

    @hybrid_property
    def timestamp_shamsi(self):
        utc_ts = self.timestamp.replace(tzinfo=pytz.utc)
        local_tz = pytz.timezone("Asia/Tehran")
        local_time = utc_ts.astimezone(local_tz)
        return jdatetime.datetime.fromgregorian(datetime=local_time)


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    is_active = Column(Boolean, default=True)
    total_calls = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)

    owner = relationship("User", back_populates="api_keys")


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
