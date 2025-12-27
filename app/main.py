from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

from app.core.config import settings
from app.api.routers import auth as api_auth, admin, patient, consultation_medications, labs
from app.api.routers import consultations
from app.api.routers import debug

app = FastAPI(title=settings.APP_NAME)

origins = {
    "https://web-diabetes-production.up.railway.app",
    "http://localhost:3000",
}
if settings.CORS_ORIGINS:
    origins.update(o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_auth.router, tags=["auth"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(patient.router, prefix="/patient", tags=["patient"])
app.include_router(consultation_medications.router, tags=["medications"])
app.include_router(labs.router, tags=["labs"])
app.include_router(consultations.router, tags=["consultations"])
app.include_router(debug.router, tags=["debug"])
