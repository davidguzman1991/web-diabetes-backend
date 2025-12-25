from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/debug/db")
def debug_db(db: Session = Depends(get_db)):
    if str(settings.ENV).lower() != "development":
        raise HTTPException(status_code=404, detail="Not found")

    response = {
        "database": None,
        "schema": None,
        "alembic_version": None,
        "catalogo_labs_exists": False,
        "catalogo_labs_count": None,
    }

    response["database"] = db.execute(text("select current_database()")).scalar()
    response["schema"] = db.execute(text("select current_schema()")).scalar()

    try:
        response["alembic_version"] = db.execute(
            text("select version_num from alembic_version limit 1")
        ).scalar()
    except Exception:
        response["alembic_version"] = None

    try:
        exists = db.execute(
            text("select to_regclass('public.catalogo_labs')")
        ).scalar()
        response["catalogo_labs_exists"] = bool(exists)
        if exists:
            response["catalogo_labs_count"] = db.execute(
                text("select count(*) from public.catalogo_labs")
            ).scalar()
    except Exception:
        response["catalogo_labs_exists"] = False
        response["catalogo_labs_count"] = None

    return response
