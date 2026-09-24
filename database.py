from sqlalchemy import create_engine
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base
)

DATABASE_URL = "postgresql://postgres@localhost:5432/rss_reader_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
    )
Base = declarative_base()