# -*- coding: utf-8 -*-
"""
تمام روت‌های پنل ادمین (داشبورد + تب-ها)
"""
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.status import HTTP_303_SEE_OTHER

from app import crud, models, schemas
from app.dependencies import get_db, get_current_admin
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")

# -----------------------------------------------------------
#  داشبورد اصلی (دارای تب‌ها)
# -----------------------------------------------------------
@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    _: models.User = Depends(get_current_admin),
):
    """صفحه اصلی پنل مدیریت با تب‌ها"""
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})


# -----------------------------------------------------------
#  تب کاربران
# -----------------------------------------------------------
@router.get(
    "/users/partial",
    response_class=HTMLResponse,
    name="admin_users_partial",
)
def users_partial(
    request: Request,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    users = crud.get_users(db)
    return templates.TemplateResponse(
        "admin/partials/users.html",
        {"request": request, "users": users},
    )


@router.post(
    "/users/create",
    response_class=HTMLResponse,
    name="admin_users_create",
)
def users_create(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    file_limit: int = Form(5),
    token_price: float = Form(10.0),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    if crud.get_user_by_username(db, username):
        raise HTTPException(400, "نام کاربری تکراری است.")
    crud.create_user(
        db,
        schemas.UserCreate(
            username=username,
            password=password,
            role=role,
            file_limit=file_limit,
            wallet_balance=0,
            token_price=token_price,
        ),
    )
    # پس از ایجاد، لیستِ به‌روزشده را به همان تب برمی‌گردانیم
    return RedirectResponse(
        url=request.url_for("admin_users_partial"), status_code=HTTP_303_SEE_OTHER
    )


@router.post(
    "/users/{user_id}/update",
    response_class=HTMLResponse,
    name="admin_users_update",
)
def users_update(
    request: Request,
    user_id: int,
    username: str = Form(...),
    file_limit: int = Form(...),
    token_price: float = Form(...),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(404, "کاربر یافت نشد.")
    crud.update_user_details(db, db_user, username, file_limit, token_price)
    return RedirectResponse(
        url=request.url_for("admin_users_partial"), status_code=HTTP_303_SEE_OTHER
    )
