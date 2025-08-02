import os
from typing import Tuple
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GAPGPT_API_KEY")
        self.base_url = settings.AI_API_URL
        self.timeout = settings.AI_API_TIMEOUT

    @retry(
        stop=stop_after_attempt(settings.AI_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def correct_text(self, text: str) -> Tuple[str, int]:
        if not self._validate_api_key():
            return f"[AI Service Unavailable] {text}", 0

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": settings.AI_MODEL_NAME,
            "messages": [
                {"role": "system", "content": settings.AI_SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            "temperature": settings.AI_TEMPERATURE
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            return (
                data["choices"][0]["message"]["content"].strip(),
                data["usage"]["total_tokens"]
            )
        except Exception as e:
            print(f"AI API Error: {e}")
            raise  # برای مدیریت توسط retry

    def _validate_api_key(self) -> bool:
        if not self.api_key or "YourActual" in self.api_key:
            print("Invalid API Key Configuration")
            return False
        return True

# تابع اصلی برای سازگاری با کد قدیمی
def correct_text_with_ai(text: str, user_price: float = 0) -> Tuple[str, int]:
    return AIService().correct_text(text)