import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

def _normalize_database_url(url: str) -> str:
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

def _get_raw_database_url() -> str | None:
    return os.getenv("DATABASE_URL") or os.getenv("DATABASE_PUBLIC_URL")


def get_database_url() -> str:
    raw_url = _get_raw_database_url()
    if not raw_url:
        raise RuntimeError("DATABASE_URL is not set")
    return _normalize_database_url(raw_url)


engine = create_engine(get_database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)

Base = declarative_base()
