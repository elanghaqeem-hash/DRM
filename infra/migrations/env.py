"""Alembic migrations: explicit DATABASE_URL, never a production default."""
import os
from alembic import context
from sqlalchemy import create_engine, pool

config = context.config
url = os.environ.get("DATABASE_URL")
if not url:
    raise RuntimeError("DATABASE_URL required")
url = url.replace("postgresql://", "postgresql+psycopg://", 1)


def run_migrations_online():
    engine = create_engine(url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=None, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    context.configure(url=url, literal_binds=True, target_metadata=None)
    with context.begin_transaction():
        context.run_migrations()
else:
    run_migrations_online()
