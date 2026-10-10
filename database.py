import os
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base
)

# Gets database URL from Docker compose file (compose.yaml)
# as environment variable POSTGRES_DATABASE_URL.
# By default, if no such variable provided, it launches
# from localhost

POSTGRES_DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL"
    "postgresql+psycopg://postgres:postgres@localhost:5432/rss_reader_db"
    )

engine = create_engine(POSTGRES_DATABASE_URL)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
    )
Base = declarative_base()