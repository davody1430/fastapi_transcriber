from __future__ import annotations
import os
import time
from pathlib import Path
from typing import Dict, List, Optional
import speech_recognition as sr
from pydub import AudioSegment
from app.core.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential

class AudioProcessor:
    def __init__(self):
        self.chunk_sec = settings.AUDIO_CHUNK_SIZE  # ثانیه
        self.default_lang = settings.DEFAULT_AUDIO_LANG
        self.recognizer = sr.Recognizer()
        self.temp_files: List[Path] = []

    def __del__(self):
        """پاکسازی خودکار فایل‌های موقت هنگام تخریب شیء"""
        self.cleanup()

    def cleanup(self):
        """حذف فایل‌های موقت"""
        for file in self.temp_files:
            try:
                if file.exists():
                    file.unlink()
            except Exception as e:
                print(f"Error deleting temp file {file}: {e}")

    @staticmethod
    def split_audio(file_path: Path) -> List[Path]:
        """تقسیم فایل صوتی به قطعات کوچکتر"""
        audio = AudioSegment.from_file(file_path)
        chunk_length_ms = 50 * 1000  # 50 ثانیه
        chunks = []
    
        for i, start in enumerate(range(0, len(audio), chunk_length_ms)):
            end = start + chunk_length_ms
            chunk = audio[start:end]
            chunk_path = file_path.with_suffix(f".part{i}.wav")
            chunk.export(chunk_path, format="wav")
            chunks.append(chunk_path)
    
        return chunks

    @retry(
        stop=stop_after_attempt(settings.AUDIO_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    def _transcribe_chunk(self, chunk_path: Path, language: str) -> str:
        """تبدیل یک قطعه صوتی به متن"""
        with sr.AudioFile(str(chunk_path)) as src:
            audio_data = self.recognizer.record(src)
            return self.recognizer.recognize_google(audio_data, language=language)

    def transcribe_audio(
        self,
        file_path: str | Path,
        language: Optional[str] = None,
    ) -> List[Dict]:
        """تبدیل فایل صوتی به متن"""
        file_path = Path(file_path).expanduser().resolve()
        segments: List[Dict] = []
        language = language or self.default_lang

        try:
            parts = self.split_audio(file_path)
            
            for idx, part_path in enumerate(parts):
                start_sec = idx * self.chunk_sec
                end_sec = start_sec + self.chunk_sec
                transcript = ""

                try:
                    transcript = self._transcribe_chunk(part_path, language)
                except sr.UnknownValueError:
                    transcript = f"({self.sec_to_mmss(start_sec)}-{self.sec_to_mmss(end_sec)})"
                except sr.RequestError as e:
                    print(f"API Error for chunk {idx}: {e}")
                    raise

                segments.append({
                    "start": start_sec,
                    "end": end_sec,
                    "text": transcript
                })

            return segments
        finally:
            self.cleanup()

    @staticmethod
    def sec_to_mmss(seconds: int) -> str:
        """تبدیل ثانیه به فرمت MM:SS"""
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

# سازگاری با کد قدیمی
def transcribe_audio_google(*args, **kwargs):
    return AudioProcessor().transcribe_audio(*args, **kwargs)

# توابع با نام قدیمی برای سازگاری
_split_audio = AudioProcessor.split_audio
_sec_to_mmss = AudioProcessor.sec_to_mmss