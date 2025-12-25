"""add categoria and orden to catalogo_labs

Revision ID: 8c2f1a7d3b10
Revises: 7a1c0f6b2d3c
Create Date: 2025-12-24 12:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = "8c2f1a7d3b10"
down_revision = "7a1c0f6b2d3c"
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


def upgrade() -> None:
    op.execute(
        "alter table public.catalogo_labs add column if not exists categoria varchar(50) not null default 'general'"
    )
    op.execute(
        "alter table public.catalogo_labs add column if not exists orden integer not null default 0"
    )
    op.execute("alter table public.catalogo_labs alter column activo set default true")
    op.execute(
        "create index if not exists ix_catalogo_labs_orden on public.catalogo_labs (orden)"
    )
    op.execute(
        "update public.catalogo_labs set categoria = 'general' where categoria is null"
    )
    op.execute(
        "update public.catalogo_labs set orden = 0 where orden is null"
    )

    conn = op.get_bind()
    for index, (nombre, unidad) in enumerate(LABS):
        conn.execute(
            sa.text(
                "insert into public.catalogo_labs "
                "(id, nombre, unidad, categoria, orden, activo) "
                "values (:id, :nombre, :unidad, 'general', :orden, true) "
                "on conflict (nombre) do update set "
                "unidad = excluded.unidad, "
                "categoria = excluded.categoria, "
                "orden = excluded.orden, "
                "activo = true"
            ),
            {
                "id": uuid.uuid4(),
                "nombre": nombre,
                "unidad": unidad,
                "orden": index,
            },
        )


def downgrade() -> None:
    pass
