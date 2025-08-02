import math
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Request,
    Form,
    Query,
    HTTPException,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app import dependencies, models, schemas, crud
from app.templating import templates

router = APIRouter(
    prefix="/admin",
    tags=["Admin Panel"],
    dependencies=[Depends(dependencies.get_current_active_admin)],
)

# ══════════════════════════ HUB (صفحهٔ اصلی با تب‌ها)
@router.get("/hub", response_class=HTMLResponse)
async def admin_hub_page(
    request: Request,
    user_search: Optional[str] = Query(None),
    transaction_search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    db: Session = Depends(dependencies.get_db),
    current_admin: models.User = Depends(dependencies.get_current_active_admin),
):
    users_list = crud.get_users(db, username_filter=user_search)
    transcription_list = crud.get_all_transcriptions(db, skip=0, limit=100)

    skip_tx = (page - 1) * settings.PAGE_SIZE
    tx_total_items = crud.get_all_transactions_count(db, username_filter=transaction_search)
    transactions_list = crud.get_all_transactions(
        db,
        username_filter=transaction_search,
        skip=skip_tx,
        limit=settings.PAGE_SIZE,
    )
    tx_total_pages = max(math.ceil(tx_total_items / settings.PAGE_SIZE), 1)

    pages = {
        "about_page": "درباره ما",
        "terms_page": "قوانین و مقررات",
        "faq_page": "سؤال‌های متداول",
        "pricing_page": "تعرفه‌ها",
    }

    return templates.TemplateResponse(
        "admin_hub.html",
        {
            "request": request,
            "user": current_admin,
            "users": users_list,
            "user_search": user_search,
            "transcriptions": transcription_list,
            "transactions": transactions_list,
            "transaction_search": transaction_search,
            "trans_current_page": page,
            "trans_total_pages": tx_total_pages,
            "pages": pages,
        },
    )

# ────────────────────────── MANAGE USERS
@router.get("/manage-users", response_class=HTMLResponse)
async def admin_manage_users_page(
    request: Request,
    user_search: Optional[str] = Query(None),
    partial: int = Query(0),
    db: Session = Depends(dependencies.get_db),
    current_admin: models.User = Depends(dependencies.get_current_active_admin),
):
    users_list = crud.get_users(db, username_filter=user_search)

    ctx = {
        "request": request,
        "user": current_admin,
        "users": users_list,
        "user_search": user_search,
    }
    tpl = "partials/manage_users_partial.html" if partial else "admin_manage_users.html"
    return templates.TemplateResponse(tpl, ctx)


@router.post("/create_user")
async def admin_create_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: models.Role = Form(...),
    file_limit: int = Form(...),
    wallet_balance: float = Form(0.0),
    token_price: float = Form(10.0),
    db: Session = Depends(dependencies.get_db),
    current_admin: models.User = Depends(dependencies.get_current_active_admin),
):
    if crud.get_user_by_username(db, username=username):
        users_list = crud.get_users(db)
        return templates.TemplateResponse(
            "admin_manage_users.html",
            {
                "request": request,
                "user": current_admin,
                "users": users_list,
                "error": f"نام کاربری «{username}» قبلاً ثبت شده است.",
            },
        )

    user_in = schemas.UserCreate(
        username=username,
        password=password,
        role=role,
        file_limit=file_limit,
        wallet_balance=wallet_balance,
        token_price=token_price,
    )
    crud.create_user(db, user_in)

    return RedirectResponse(
        url="/admin/manage-users?msg=user-created",
        status_code=status.HTTP_303_SEE_OTHER,
    )
# ────────────────────────── ALL ACTIVITIES
@router.get("/all-activities", response_class=HTMLResponse)
async def admin_all_activities_page(
    request: Request,
    page: int = Query(1, gt=0),
    partial: int = Query(0),
    db: Session = Depends(dependencies.get_db),
    current_admin: models.User = Depends(dependencies.get_current_active_admin),
):
    skip = (page - 1) * settings.PAGE_SIZE
    total_items = crud.get_all_transcriptions_count(db)
    activities = crud.get_all_transcriptions(db, skip=skip, limit=settings.PAGE_SIZE)
    total_pages = max(math.ceil(total_items / settings.PAGE_SIZE), 1)

    ctx = {
        "request": request,
        "user": current_admin,
        "activities": activities,
        "current_page_acts": page,
        "total_pages_acts": total_pages,
    }
    tpl = "partials/all_activities_partial.html" if partial else "admin_all_activities.html"
    return templates.TemplateResponse(tpl, ctx)


# ────────────────────────── ALL TRANSACTIONS
@router.get("/all-transactions", response_class=HTMLResponse)
async def admin_all_transactions_page(
    request: Request,
    page: int = Query(1, gt=0),
    transaction_search: Optional[str] = Query(None),
    partial: int = Query(0),
    db: Session = Depends(dependencies.get_db),
    current_admin: models.User = Depends(dependencies.get_current_active_admin),
):
    skip = (page - 1) * settings.PAGE_SIZE
    total_items = crud.get_all_transactions_count(db, username_filter=transaction_search)
    transactions_list = crud.get_all_transactions(
        db,
        username_filter=transaction_search,
        skip=skip,
        limit=settings.PAGE_SIZE,
    )
    total_pages = max(math.ceil(total_items / settings.PAGE_SIZE), 1)

    ctx = {
        "request": request,
        "user": current_admin,
        "transactions": transactions_list,
        "current_page_txs": page,
        "total_pages_txs": total_pages,
        "transaction_search": transaction_search,
    }
    tpl = "partials/all_transactions_partial.html" if partial else "admin_all_transactions.html"
    return templates.TemplateResponse(tpl, ctx)


# ────────────────────────── CONTENT MANAGEMENT
@router.get("/content", response_class=HTMLResponse)
async def content_management_page(
    request: Request,
    partial: int = Query(0),
    current_admin: models.User = Depends(dependencies.get_current_active_admin),
):
    editable_pages = {
        "about_page": "درباره ما",
        "terms_page": "قوانین و مقررات",
        "faq_page": "سؤال‌های متداول",
        "pricing_page": "تعرفه‌ها",
    }

    ctx = {"request": request, "user": current_admin, "pages": editable_pages}
    tpl = "partials/content_mgt_partial.html" if partial else "admin_content_management.html"
    return templates.TemplateResponse(tpl, ctx)


@router.get("/content/edit/{page_key}", response_class=HTMLResponse)
async def edit_content_form(
    page_key: str,
    request: Request,
    db: Session = Depends(dependencies.get_db),
    current_admin: models.User = Depends(dependencies.get_current_active_admin),
):
    page_titles = {
        "about_page": "درباره ما",
        "terms_page": "قوانین و مقررات",
        "faq_page": "سؤال‌های متداول",
        "pricing_page": "تعرفه‌ها",
    }

    setting = crud.get_setting(db, page_key)
    content_val = setting.value if setting else ""

    return templates.TemplateResponse(
        "admin_edit_content.html",
        {
            "request": request,
            "user": current_admin,
            "page_key": page_key,
            "page_title": page_titles.get(page_key, "صفحه"),
            "content": content_val,
        },
    )


@router.post("/content/edit/{page_key}")
async def handle_edit_content(
    page_key: str,
    content: str = Form(...),
    db: Session = Depends(dependencies.get_db),
    current_admin: models.User = Depends(dependencies.get_current_active_admin),
):
    crud.upsert_setting(db, key=page_key, value=content)
    return RedirectResponse(
        url=f"/admin/content/edit/{page_key}?msg=content-updated",
        status_code=status.HTTP_303_SEE_OTHER,
    )

