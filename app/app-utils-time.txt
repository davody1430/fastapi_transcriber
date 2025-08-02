from datetime import datetime, timezone, timedelta

def now_tehran() -> datetime:
    """Get current time in Tehran timezone (UTC+3:30)"""
    return datetime.now(timezone(timedelta(hours=3, minutes=30)))