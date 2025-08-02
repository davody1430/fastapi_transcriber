# alembic/env.py
import sys, os, pathlib
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ---------- دسترسی Alembic به کد پروژه ----------
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]   # .../fastapi_transcriber
sys.path.insert(0, str(BASE_DIR))                        # افزودن به PYTHONPATH

# حالا مدل‌ها را وارد می‌کنیم
from app.database import Base        # ← اگر ماژولِ تو app است
target_metadata = Base.metadata      # ← بسیار مهم

# --------------------------------------------------

# این شیء تنظیمات Alembic است
config = context.config

# تنظیم لاگینگ (پیش‌فرض Alembic)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --------- بقیهٔ فایل همان کد ژنراتور Alembic است ---------
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
