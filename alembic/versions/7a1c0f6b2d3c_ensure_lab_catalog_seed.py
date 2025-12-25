"""ensure lab catalog seed

Revision ID: 7a1c0f6b2d3c
Revises: 6f2e9a6b0e2f
Create Date: 2025-12-24 11:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = "7a1c0f6b2d3c"
down_revision = "6f2e9a6b0e2f"
branch_labels = None
depends_on = None


LABS = [
    ("Glucosa ayunas", "mg/dL", None, None),
    ("Glucosa postprandial", "mg/dL", None, None),
    ("HbA1c", "%", None, None),
    ("Creatinina", "mg/dL", None, None),
    ("eGFR", "mL/min/1.73m2", None, None),
    ("UACR", "mg/g", None, None),
    ("Colesterol total", "mg/dL", None, None),
    ("LDL", "mg/dL", None, None),
    ("HDL", "mg/dL", None, None),
    ("Trigliceridos", "mg/dL", None, None),
    ("ALT/TGP", "U/L", None, None),
    ("AST/TGO", "U/L", None, None),
]


def upgrade() -> None:
    op.execute(
        """
        create table if not exists public.catalogo_labs (
            id uuid primary key,
            nombre text not null unique,
            unidad text null,
            rango_ref_min double precision null,
            rango_ref_max double precision null,
            categoria text null,
            orden integer not null default 0,
            activo boolean not null default true
        )
        """
    )
    op.execute(
        "create index if not exists ix_catalogo_labs_nombre on public.catalogo_labs (nombre)"
    )
    op.execute(
        "alter table public.catalogo_labs add column if not exists categoria text"
    )
    op.execute(
        "alter table public.catalogo_labs add column if not exists orden integer default 0"
    )

    conn = op.get_bind()
    for nombre, unidad, rango_min, rango_max in LABS:
        conn.execute(
            sa.text(
                "insert into public.catalogo_labs (id, nombre, unidad, rango_ref_min, rango_ref_max, activo) "
                "values (:id, :nombre, :unidad, :rango_min, :rango_max, true) "
                "on conflict (nombre) do update set "
                "unidad = excluded.unidad, "
                "rango_ref_min = excluded.rango_ref_min, "
                "rango_ref_max = excluded.rango_ref_max, "
                "activo = true"
            ),
            {
                "id": uuid.uuid4(),
                "nombre": nombre,
                "unidad": unidad,
                "rango_min": rango_min,
                "rango_max": rango_max,
            },
        )


def downgrade() -> None:
    pass
