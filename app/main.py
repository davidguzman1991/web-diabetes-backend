import logging
from sqlalchemy import text
from sqlalchemy.engine import make_url
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

from app.core.config import settings
from app.api.routers import auth as api_auth, admin, patient, consultation_medications, labs
from app.api.routers import consultations
from app.core.database import SessionLocal, get_database_url
from app.models.catalog_lab import CatalogLab
from app.api.routers import debug
from app.routes import auth

app = FastAPI(title=settings.APP_NAME)

if settings.CORS_ORIGINS:
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
else:
    origins = []

if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth.router)
app.include_router(api_auth.router, tags=["auth"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(patient.router, prefix="/patient", tags=["patient"])
app.include_router(consultation_medications.router, tags=["medications"])
app.include_router(labs.router, tags=["labs"])
app.include_router(consultations.router, tags=["consultations"])
app.include_router(debug.router, tags=["debug"])


def _mask_database_url(url: str) -> str:
    parsed = make_url(url)
    if parsed.password:
        parsed = parsed.set(password="***")
    return str(parsed)


@app.on_event("startup")
def log_lab_catalog_count() -> None:
    logger = logging.getLogger(__name__)
    try:
        logger.info("Database target: %s", _mask_database_url(get_database_url()))
    except Exception as exc:
        logger.warning("Database target unavailable: %s", exc)

    db = SessionLocal()
    try:
        db.execute(text("select 1"))
        count = db.query(CatalogLab).count()
        logger.info("Lab catalog count: %s", count)
    except Exception:
        logger.exception("Database check failed on startup")
    finally:
        db.close()
