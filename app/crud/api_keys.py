# app/crud/api_keys.py
# مدیریت کلیدهای API
import uuid
from sqlalchemy.orm import Session
from app import models

def _generate_api_key() -> str:
    return uuid.uuid4().hex + uuid.uuid4().hex

def create_api_key(db: Session, user: models.User):
    key = _generate_api_key()
    api_key = models.APIKey(key=key, owner=user)
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key

def deactivate_api_key(db: Session, api_key: models.APIKey):
    api_key.is_active = False
    db.commit()
