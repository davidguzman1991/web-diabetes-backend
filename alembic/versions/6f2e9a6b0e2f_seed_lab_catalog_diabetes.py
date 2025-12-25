"""seed lab catalog diabetes

Revision ID: 6f2e9a6b0e2f
Revises: 4c8b8f1e0d2a
Create Date: 2025-12-24 10:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = "6f2e9a6b0e2f"
down_revision = "4c8b8f1e0d2a"
branch_labels = None
depends_on = None


LABS = [
    ("Glucosa ayunas", "mg/dL"),
    ("Glucosa postprandial", "mg/dL"),
    ("HbA1c", "%"),
    ("Creatinina", "mg/dL"),
    ("eGFR", "mL/min/1.73m2"),
    ("UACR", "mg/g"),
    ("Colesterol total", "mg/dL"),
    ("LDL", "mg/dL"),
    ("HDL", "mg/dL"),
    ("Trigliceridos", "mg/dL"),
    ("ALT/TGP", "U/L"),
    ("AST/TGO", "U/L"),
]


RENAMES = {
    "glucosa ayunas": ("Glucosa ayunas", "mg/dL"),
    "glucosa en ayunas": ("Glucosa ayunas", "mg/dL"),
    "tfg": ("eGFR", "mL/min/1.73m2"),
    "filtrado glomerular": ("eGFR", "mL/min/1.73m2"),
    "egfr": ("eGFR", "mL/min/1.73m2"),
    "uacr": ("UACR", "mg/g"),
    "microalbuminuria": ("UACR", "mg/g"),
    "colesterol ldl": ("LDL", "mg/dL"),
    "ldl": ("LDL", "mg/dL"),
    "colesterol total": ("Colesterol total", "mg/dL"),
    "hdl": ("HDL", "mg/dL"),
    "trigliceridos": ("Trigliceridos", "mg/dL"),
    "alt": ("ALT/TGP", "U/L"),
    "tgp": ("ALT/TGP", "U/L"),
    "ast": ("AST/TGO", "U/L"),
    "tgo": ("AST/TGO", "U/L"),
}


def upgrade() -> None:
    conn = op.get_bind()
    for old_lower, (new_name, unidad) in RENAMES.items():
        conn.execute(
            sa.text(
                "update catalogo_labs set nombre = :new_name, unidad = :unidad "
                "where lower(nombre) = :old_name"
            ),
            {"new_name": new_name, "unidad": unidad, "old_name": old_lower},
        )

    for nombre, unidad in LABS:
        conn.execute(
            sa.text(
                "insert into catalogo_labs (id, nombre, unidad, activo) "
                "values (:id, :nombre, :unidad, true) "
                "on conflict (nombre) do nothing"
            ),
            {"id": uuid.uuid4(), "nombre": nombre, "unidad": unidad},
        )


def downgrade() -> None:
    pass
