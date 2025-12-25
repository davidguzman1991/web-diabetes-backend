import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.dependencies import require_admin
from app.crud import consultations as consultation_crud
from app.crud import consulta_labs as consulta_labs_crud
from app.crud import lab_catalog as lab_catalog_crud
from app.crud import patients as patient_crud
from app.models.consulta_lab import ConsultaLab
from app.models.catalog_lab import CatalogLab
from app.schemas.consulta_lab import ConsultaLabCreate, ConsultaLabOut
from app.schemas.lab_catalog import CatalogLabCreate, CatalogLabOut, CatalogLabUpdate

logger = logging.getLogger(__name__)

router = APIRouter()


def _format_rango(min_value: float | None, max_value: float | None) -> str | None:
    if min_value is None and max_value is None:
        return None
    if min_value is None:
        return f"<= {max_value}"
    if max_value is None:
        return f">= {min_value}"
    return f"{min_value} - {max_value}"


def _list_catalog_sql(db: Session) -> list[CatalogLabOut]:
    rows = db.execute(
        text(
            """
            select id, nombre, unidad, rango_ref_min, rango_ref_max, activo, categoria, orden
            from public.catalogo_labs
            where activo = true
            order by orden, nombre
            """
        )
    ).mappings()
    response: list[CatalogLabOut] = []
    for row in rows:
        response.append(
            CatalogLabOut(
                id=str(row["id"]),
                nombre=row["nombre"],
                unidad=row["unidad"],
                rango_ref_min=row["rango_ref_min"],
                rango_ref_max=row["rango_ref_max"],
                activo=bool(row["activo"]),
                categoria=row.get("categoria"),
                orden=row.get("orden"),
            )
        )
    return response


def _list_catalog_safe(db: Session) -> list[CatalogLabOut]:
    try:
        return _list_catalog_sql(db)
    except (ProgrammingError, OperationalError) as exc:
        logger.warning("Lab catalog unavailable: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Catalogo de laboratorios no disponible. Ejecuta alembic upgrade head.",
        ) from exc


def _get_consulta_or_404(db: Session, consulta_id: str):
    consulta = consultation_crud.get(db, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no existe")
    return consulta


def _ensure_consulta_access(db: Session, consulta_id: str, current_user) -> None:
    role = str(getattr(current_user, "role", "")).strip().lower()
    if role == "admin":
        return
    if role != "patient":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    consulta = _get_consulta_or_404(db, consulta_id)
    patient = patient_crud.get_by_cedula(db, current_user.username)
    if not patient or str(patient.id) != str(consulta.patient_id):
        raise HTTPException(status_code=403, detail="Acceso denegado")


@router.get("/labs/catalogo")
def list_catalog(db: Session = Depends(get_db)):
    try:
        rows = (
            db.query(CatalogLab)
            .filter(CatalogLab.activo == True)
            .order_by(CatalogLab.orden.asc(), CatalogLab.nombre.asc())
            .all()
        )
        return [
            {
                "id": str(row.id),
                "nombre": row.nombre,
                "unidad": row.unidad,
                "rango_ref_min": row.rango_ref_min,
                "rango_ref_max": row.rango_ref_max,
                "categoria": row.categoria,
                "orden": row.orden,
                "activo": row.activo,
            }
            for row in rows
        ]
    except (ProgrammingError, OperationalError) as exc:
        logger.exception("Catalogo labs unavailable")
        raise HTTPException(
            status_code=503,
            detail="catalogo_labs no existe o no tiene columnas esperadas; revisa DATABASE_URL y alembic upgrade head",
        ) from exc
    except Exception as exc:
        logger.exception("Error loading catalogo_labs")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/labs/catalog", response_model=list[CatalogLabOut])
def list_catalog_auth(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return _list_catalog_safe(db)


@router.get("/lab-catalog", response_model=list[CatalogLabOut])
def list_catalog_alias(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return _list_catalog_safe(db)


@router.post("/labs/catalogo", response_model=CatalogLabOut, status_code=status.HTTP_201_CREATED)
def create_catalog_lab(
    data: CatalogLabCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    existing = lab_catalog_crud.get_by_name_normalized(db, data.nombre)
    if existing:
        raise HTTPException(status_code=409, detail="Laboratorio ya existe")
    return lab_catalog_crud.create(db, data)


@router.put("/labs/catalogo/{lab_id}", response_model=CatalogLabOut)
def update_catalog_lab(
    lab_id: str,
    data: CatalogLabUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    lab = lab_catalog_crud.get(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Laboratorio no existe")
    return lab_catalog_crud.update(db, lab, data)


@router.get("/consultas/{consulta_id}/labs", response_model=list[ConsultaLabOut])
def list_consulta_labs(
    consulta_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _ensure_consulta_access(db, consulta_id, current_user)
    labs = consulta_labs_crud.list_by_consulta(db, consulta_id)
    response: list[ConsultaLabOut] = []
    for lab in labs:
        response.append(
            ConsultaLabOut(
                id=str(lab.id),
                consulta_id=str(lab.consulta_id),
                lab_id=str(lab.lab_id),
                lab_nombre=lab.lab.nombre if lab.lab else "",
                valor_num=lab.valor_num,
                valor_texto=lab.valor_texto,
                unidad_snapshot=lab.unidad_snapshot,
                rango_ref_snapshot=lab.rango_ref_snapshot,
                creado_en=lab.creado_en,
            )
        )
    return response


# Example payload:
# [
#   {"lab_id": "<uuid>", "valor_num": 110.0},
#   {"lab_id": "<uuid>", "valor_num": 5.7}
# ]
@router.post("/consultas/{consulta_id}/labs", response_model=list[ConsultaLabOut])
def save_consulta_labs(
    consulta_id: str,
    data: list[ConsultaLabCreate],
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    consulta = _get_consulta_or_404(db, consulta_id)
    consulta_labs_crud.delete_by_consulta(db, consulta_id)

    items = []
    for item in data:
        lab = lab_catalog_crud.get(db, item.lab_id)
        if not lab:
            lab = lab_catalog_crud.get_by_name_normalized(db, item.lab_id)
        if not lab:
            lab = lab_catalog_crud.find_by_name_contains(db, item.lab_id)
        if not lab:
            raise HTTPException(status_code=400, detail="Laboratorio no pertenece al catalogo")
        rango_snapshot = _format_rango(lab.rango_ref_min, lab.rango_ref_max)
        items.append(
            ConsultaLab(
                consulta_id=consulta.id,
                lab_id=lab.id,
                valor_num=item.valor_num,
                valor_texto=None,
                unidad_snapshot=lab.unidad,
                rango_ref_snapshot=rango_snapshot,
            )
        )

    created = consulta_labs_crud.create_many(db, items) if items else []
    logger.info("Saved %s labs for consulta %s", len(created), consulta_id)

    response: list[ConsultaLabOut] = []
    for lab in created:
        response.append(
            ConsultaLabOut(
                id=str(lab.id),
                consulta_id=str(lab.consulta_id),
                lab_id=str(lab.lab_id),
                lab_nombre=lab.lab.nombre if lab.lab else "",
                valor_num=lab.valor_num,
                valor_texto=lab.valor_texto,
                unidad_snapshot=lab.unidad_snapshot,
                rango_ref_snapshot=lab.rango_ref_snapshot,
                creado_en=lab.creado_en,
            )
        )
    return response
