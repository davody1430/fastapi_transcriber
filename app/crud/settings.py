# app/crud/settings.py
# مدیریت تنظیمات کلی برنامه
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from app import models

# دریافت تنظیمات براساس کلید
def get_setting(db: Session, key: str):
    return db.query(models.Setting).filter(models.Setting.key == key).first()

# ایجاد یا به‌روزرسانی تنظیمات
def upsert_setting(db: Session, key: str, value: str):
    try:
        setting = db.query(models.Setting).filter(models.Setting.key == key).one()
        setting.value = value
    except NoResultFound:
        setting = models.Setting(key=key, value=value)
        db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting
