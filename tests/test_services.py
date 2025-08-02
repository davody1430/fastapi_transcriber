import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from app.services.audio_processing import AudioProcessor
from app.services.ai_services import AIService

@pytest.fixture
def mock_audio_file(tmp_path):
    test_file = tmp_path / "test.wav"
    # ایجاد یک فایل صوتی تستی کوچک
    test_file.write_bytes(b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00")
    return test_file

def test_audio_processor_cleanup(mock_audio_file):
    processor = AudioProcessor()
    processor.transcribe_audio(mock_audio_file)
    assert len(processor.temp_files) > 0
    # بررسی حذف فایل‌های موقت
    for temp_file in processor.temp_files:
        assert not temp_file.exists()

def test_audio_chunk_size_config():
    processor = AudioProcessor()
    assert processor.chunk_sec == 50  # مقدار پیش‌فرض
    # تست تغییر مقدار از طریق تنظیمات
    with patch("app.core.config.settings.AUDIO_CHUNK_SIZE", 30):
        processor = AudioProcessor()
        assert processor.chunk_sec == 30

@patch("requests.post")
def test_ai_service_retry(mock_post):
    mock_post.side_effect = requests.exceptions.RequestException("Timeout")
    ai_service = AIService()
    
    with pytest.raises(requests.exceptions.RequestException):
        ai_service.correct_text("test")
    
    assert mock_post.call_count == 3  # مطابق با MAX_RETRIES