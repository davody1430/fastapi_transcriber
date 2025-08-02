# app/crud/transactions.py
from sqlalchemy.orm import Session
from app import models
from app.utils.time import now_tehran  # تغییر اینجا

def create_transaction(db: Session, user_id: int, amount: float, description: str, token_price: float | None = None):
    tx = models.Transaction(
        user_id=user_id,
        amount=amount,
        description=description,
        token_price_at_transaction=token_price,
        timestamp=now_tehran(),  # تغییر اینجا
    )
    db.add(tx)
    return tx

def adjust_user_balance(db: Session, user: models.User, amount: float, description: str):
    if amount == 0:
        return
    user.wallet_balance += amount
    create_transaction(db, user.id, amount, description, user.token_price)
    db.commit()
    db.refresh(user)

def debit_from_wallet(db: Session, user: models.User, cost: float, description: str):
    db.refresh(user)
    if user.wallet_balance < cost:
        raise ValueError("موجودی ناکافی برای این عملیات")
    user.wallet_balance -= cost
    create_transaction(db, user.id, -cost, description, user.token_price)
    db.commit()
    db.refresh(user)