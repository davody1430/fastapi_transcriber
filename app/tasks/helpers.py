# app/tasks/helpers.py
# توابع کمکی مشترک برای پردازش‌ها
from typing import Any
from app.services.ai_services import correct_text_with_ai

# تبدیل خروجی به متن تمیز
def to_clean_string(raw: Any) -> str:
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, list):
        parts = []
        for item in raw:
            parts.append(str(item.get("text", item)) if isinstance(item, dict) else str(item))
        return "\n".join(p for p in parts if p).strip()
    return str(raw).strip()

# اصلاح یک تکه متن توسط AI
def correct_single_text_chunk(task_data: tuple[int, str, float]):
    idx, chunk, price = task_data
    corrected, used = correct_text_with_ai(chunk, price)
    return idx, corrected, used
