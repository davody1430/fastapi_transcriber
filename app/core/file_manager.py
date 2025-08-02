from pathlib import Path
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class FileManager:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def get_upload_path(self, filename: str) -> Path:
        """مسیر کامل فایل آپلود شده را برمی‌گرداند"""
        return self.upload_dir / filename

    def save_file(self, file_content: bytes, filename: str) -> Path:
        """ذخیره فایل با مدیریت خطا"""
        file_path = self.get_upload_path(filename)
        try:
            with open(file_path, "wb") as f:
                f.write(file_content)
            return file_path
        except Exception as e:
            logger.error(f"Failed to save file {filename}: {e}")
            raise

    def delete_file(self, filename: str) -> bool:
        """حذف فایل با مدیریت خطا"""
        file_path = self.get_upload_path(filename)
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {filename}: {e}")
            return False

file_manager = FileManager()