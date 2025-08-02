# app/services/text_processing.py

import docx

def extract_text_from_docx(file_path: str) -> str:
    """متن را از یک فایل .docx استخراج می‌کند."""
    try:
        document = docx.Document(file_path)
        return "\n".join([para.text for para in document.paragraphs])
    except Exception as e:
        print(f"Error reading docx file {file_path}: {e}")
        return ""

def split_text_into_chunks(text: str, chunk_size: int = 2500):
    """یک متن طولانی را به قطعات کوچکتر با اندازه مشخص تقسیم می‌کند."""
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]
