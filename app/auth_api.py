from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from .database import get_db
from .models import APIKey


def get_current_service_user(
    db: Session = Depends(get_db),
    authorization: str = Header(None, alias="Authorization"),
):
    """
    دریافت Bearer <token> و تحویل یوزر سرویس
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing token")
    token = authorization.split(" ", 1)[1].strip()

    api_key = (
        db.query(APIKey)
        .filter(APIKey.key == token, APIKey.is_active.is_(True))
        .first()
    )
    if not api_key:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid token")

    return api_key.owner  # -> models.User
