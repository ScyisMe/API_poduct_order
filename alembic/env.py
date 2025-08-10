import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.engine import Connection

from alembic import context

# Alembic конфігурація
config = context.config

# Налаштування логування
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Підключення моделей
from model.base import Base
from model.config import setting

target_metadata = Base.metadata

# Встановлення URL до БД із конфігу (асинхронний)
config.set_main_option("sqlalchemy.url", setting.db.url)


def run_migrations_offline() -> None:
    """Запуск міграцій в offline-режимі."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Виклик синхронних міграцій усередині async контексту."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Асинхронний запуск міграцій (online)."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Точка входу для online-режиму."""
    asyncio.run(run_async_migrations())


# Запуск залежно від режиму
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
