# app/routers/user.py

import math
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.core.config import settings
from app.messages import (
    PASSWORD_CHANGE_SUCCESS,
    PASSWORD_CHANGE_ERROR,
    INVALID_CREDENTIALS
)
from .. import crud, models, dependencies, auth
from ..templating import templates

router = APIRouter(
    tags=["User Pages & Dashboard"],
    dependencies=[Depends(dependencies.get_current_user_from_cookie)]
)

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    current_user: models.User = Depends(dependencies.get_current_user_from_cookie),
    db: Session = Depends(dependencies.get_db)
):
    """صفحه داشبورد اصلی کاربران"""
    transcriptions = crud.get_user_transcriptions(db, user_id=current_user.id, skip=0, limit=10)
    return templates.TemplateResponse(
        "user_dashboard.html",
        {
            "request": request,
            "user": current_user,
            "transcriptions": transcriptions,
        },
    )

@router.get("/my-dashboard", response_class=HTMLResponse)
async def my_dashboard_router(
    request: Request,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user_from_cookie),
):
    """
    مسیر مشترک برای بازگشت از عملیات‌هایی مانند لغو فایل یا ایجاد تغییر.
    بر اساس نقش کاربر، به داشبورد مناسب هدایت می‌شود.
    """
    if current_user.role == models.Role.ADMIN:
        # هدایت به داشبورد ادمین
        return RedirectResponse(url="/admin/hub", status_code=303)

    # نمایش داشبورد کاربر عادی
    transcriptions = crud.get_user_transcriptions(db, user_id=current_user.id, skip=0, limit=10)
    return templates.TemplateResponse(
        "user_dashboard.html",
        {
            "request": request,
            "user": current_user,
            "transcriptions": transcriptions,
        },
    )

@router.get("/users/{user_id}/transcriptions", response_class=HTMLResponse)
async def admin_view_user_transcriptions(
    user_id: int,
    request: Request,
    page: int = Query(1, gt=0),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user_from_cookie),
):
    skip = (page - 1) * settings.PAGE_SIZE
    total_items = crud.get_user_transcriptions_count(db, user_id=user_id)
    transcriptions = crud.get_user_transcriptions(
        db, user_id=user_id, skip=skip, limit=settings.PAGE_SIZE
    )
    total_pages = math.ceil(total_items / settings.PAGE_SIZE) if total_items > 0 else 1

    return templates.TemplateResponse(
        "admin_user_transcriptions.html",
        {
            "request": request,
            "transcriptions": transcriptions,
            "current_page": page,
            "total_pages": total_pages,
        },
    )

@router.post("/change-password")
async def handle_change_password(
    request: Request,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user_from_cookie),
):
    form = await request.form()
    current_password = form.get("current_password")
    new_password = form.get("new_password")

    if not auth.verify_password(current_password, current_user.hashed_password):
        return templates.TemplateResponse(
            "change_password.html",
            {
                "request": request,
                "error": INVALID_CREDENTIALS,
            },
        )

    crud.update_user_password(db, current_user, new_password)
    return templates.TemplateResponse(
        "change_password.html",
        {
            "request": request,
            "msg": PASSWORD_CHANGE_SUCCESS,
        },
    )
