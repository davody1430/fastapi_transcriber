from datetime import timedelta
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.config import settings
from app.messages import INVALID_CREDENTIALS
from .. import crud, auth, models, dependencies
from ..templating import templates

router = APIRouter(tags=["Authentication"])

@router.post("/token")
async def login_for_access_token(
    request: Request, 
    db: Session = Depends(dependencies.get_db)
):
    form = await request.form()
    username, password = form.get("username"), form.get("password")
    
    user = crud.get_user_by_username(db, username=username)
    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": INVALID_CREDENTIALS
        })

    # تنظیم زمان انقضای توکن از تنظیمات مرکزی
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return response