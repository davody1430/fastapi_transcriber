# reset_password.py
"""
تغییر یا ریست رمز عبور یک کاربر موجود در پایگاه‌داده.

روش اجرا:
    python reset_password.py <username> [<new_password>]

اگر <new_password> را ننویسی، اسکریپت به‌صورت تعاملی رمز را می‌پرسد
(دو بار برای تأیید) و سپس آن را هش می‌کند و در جدول users ذخیره می‌کند.
"""

from __future__ import annotations

import argparse
import sys
from getpass import getpass
from pathlib import Path

# اطمینان از دسترسی به پکیج app
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from app.database import SessionLocal
from app import models, auth


def prompt_password() -> str:
    pw1 = getpass("🔑  رمز جدید را وارد کنید: ")
    pw2 = getpass("🔑  تکرار رمز: ")
    if pw1 != pw2:
        print("❌ رمزها یکسان نیستند!")
        sys.exit(1)
    if len(pw1) < 6:
        print("❌ طول رمز باید حداقل ۶ کاراکتر باشد.")
        sys.exit(1)
    return pw1


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset password for a user.")
    parser.add_argument("username", help="نام کاربری (username) هدف")
    parser.add_argument(
        "password",
        nargs="?",
        default=None,
        help="رمز عبور جدید (اختیاری؛ در صورت عدم درج، تعاملی پرسیده می‌شود)",
    )
    args = parser.parse_args()

    new_password = args.password or prompt_password()

    db = SessionLocal()
    user = db.query(models.User).filter_by(username=args.username).first()
    if not user:
        print(f"❌ کاربر «{args.username}» پیدا نشد.")
        db.close()
        sys.exit(1)

    user.hashed_password = auth.get_password_hash(new_password)
    db.commit()
    db.close()

    print(f"✅ رمز کاربر «{args.username}» با موفقیت تغییر کرد.")


if __name__ == "__main__":
    main()
