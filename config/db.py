import os
from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL

@lru_cache(maxsize=1)
def get_engine() -> Engine:
    user = os.getenv("PG_USER")
    password = os.getenv("PG_PASS")
    if not user or not password:
        raise RuntimeError("PG_USER and PG_PASS environment variables are required.")
    url = URL.create(
        "postgresql+psycopg2", username=user, password=password,
        host=os.getenv("DB_HOST", "dazuswdpgpolc01.postgres.database.azure.com"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "polcaidashboard"),
    )
    return create_engine(url, pool_pre_ping=True, pool_recycle=1800,
                         pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
                         max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
                         connect_args={"sslmode": os.getenv("PG_SSLMODE", "require")})
