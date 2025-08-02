# app/tasks/audio.py

def parallel_audio_job(record_id: int, file_path: str, lang: str = "fa-IR"):
    """
    منطق اجرای پردازش موازی فایل صوتی
    """
    print(f"[parallel_audio_job] Processing record {record_id} with lang {lang}")
    return {"status": "ok", "record_id": record_id}
