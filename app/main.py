import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

from app.core.config import settings
from app.api.routers import auth as api_auth, admin, patient, consultation_medications, labs
from app.api.routers import consultations
from app.core.database import SessionLocal
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


@app.on_event("startup")
def log_lab_catalog_count() -> None:
    logger = logging.getLogger(__name__)
    db = SessionLocal()
    try:
        count = db.query(CatalogLab).count()
        logger.info("Lab catalog count: %s", count)
    except Exception as exc:
        logger.warning("Lab catalog count unavailable: %s", exc)
    finally:
        db.close()
