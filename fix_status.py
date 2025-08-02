# fix_status.py
"""
این اسکریپت تمام رکوردهای ترانویس که status آنها 'pending' است
را به 'queued' تبدیل می‌کند تا امکان لغو داشته باشند.
"""

from app.database import SessionLocal
from app import models

def main() -> None:
    db = SessionLocal()
    updated = (
        db.query(models.TranscriptionFile)
        .filter(models.TranscriptionFile.status == "pending")
        .update({"status": "queued"})
    )
    db.commit()
    db.close()
    print(f"✅ تعداد رکوردهای به‌روزشده: {updated}")

if __name__ == "__main__":
    main()
