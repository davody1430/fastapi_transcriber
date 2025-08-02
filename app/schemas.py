from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from .models import Role

class Token(BaseModel):
    """Schema for JWT tokens"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")

class TokenData(BaseModel):
    """Data structure for decoded token content"""
    username: Optional[str] = Field(None, description="User identifier")


# تعریف Enum برای Role هم‌راستا با models.py
class Role(str, Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"
    CUSTOMER = "customer"


# کلاس پایهٔ کاربر
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username of the user")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password of the user")
    role: Role = Field(Role.CUSTOMER, description="User role")  # ✅ با توجه به تغییر Enum
    file_limit: int = Field(5, ge=0, description="Maximum number of files user can submit")
    wallet_balance: float = Field(0.0, ge=0.0, description="User wallet balance")
    token_price: float = Field(10.0, gt=0, description="Price per token")

class UserUpdate(BaseModel):
    """Schema for updating user details"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    file_limit: Optional[int] = Field(None, ge=1)
    token_price: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = Field(None)

class UserOut(UserBase):
    id: int
    role: Role
    file_limit: int
    wallet_balance: float
    token_price: float
    is_active: bool
    created_at: datetime
    
class User(UserBase):
    """Complete user schema"""
    id: int
    role: Role
    file_limit: int
    wallet_balance: float
    token_price: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "admin",
                "role": "admin",
                "file_limit": 100,
                "wallet_balance": 1000.0,
                "token_price": 10.0,
                "is_active": True,
                "created_at": "2023-01-01T00:00:00"
            }
        }

class PasswordChange(BaseModel):
    """Schema for password change requests"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, description="New password")

class TranscriptionFileBase(BaseModel):
    """Base schema for transcription records"""
    original_filename: str = Field(..., description="Original uploaded filename")
    display_filename: str = Field(..., description="Display name in dashboard")
    language: str = Field("fa-IR", description="Language code")

class TranscriptionFileCreate(TranscriptionFileBase):
    """Schema for creating new transcription records"""
    pass

class TranscriptionFile(TranscriptionFileBase):
    """Complete transcription record schema"""
    id: int
    user_id: int
    timestamp: datetime
    timestamp_local: datetime
    status: str = Field(..., description="Processing status")
    celery_task_id: Optional[str] = Field(None, description="Celery task ID")
    raw_result_text: Optional[str] = Field(None, description="Raw transcription")
    ai_result_text: Optional[str] = Field(None, description="AI corrected text")
    final_result_text: Optional[str] = Field(None, description="Final output")
    processing_duration_seconds: Optional[int] = Field(None, description="Processing time")
    ai_token_usage: Optional[int] = Field(None, description="Tokens consumed")
    output_filename_txt: Optional[str] = Field(None, description="Text output filename")
    output_filename_docx: Optional[str] = Field(None, description="Word output filename")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "original_filename": "lecture.mp3",
                "display_filename": "Lecture Audio",
                "language": "fa-IR",
                "timestamp": "2023-01-01T00:00:00",
                "timestamp_local": "1401-10-11T03:30:00",
                "status": "completed",
                "final_result_text": "متن پیاده‌سازی شده...",
                "output_filename_txt": "1_lecture.txt",
                "output_filename_docx": "1_lecture.docx"
            }
        }

class TransactionBase(BaseModel):
    """Base transaction schema"""
    amount: float = Field(..., description="Transaction amount")
    description: str = Field(..., max_length=255, description="Transaction purpose")

class TransactionCreate(TransactionBase):
    """Schema for creating transactions"""
    token_price_at_transaction: Optional[float] = Field(None, description="Price per token at transaction time")

class Transaction(TransactionBase):
    """Complete transaction schema"""
    id: int
    user_id: int
    timestamp: datetime
    timestamp_shamsi: str
    token_price_at_transaction: Optional[float]

    class Config:
        from_attributes = True

class APIKeyInfo(BaseModel):
    """Schema for API key information"""
    key: str
    created_at: datetime
    last_used_at: Optional[datetime]
    is_active: bool
    total_calls: int
    total_tokens_used: int

    class Config:
        from_attributes = True

class SettingSchema(BaseModel):
    """Schema for application settings"""
    key: str
    value: str

    class Config:
        from_attributes = True