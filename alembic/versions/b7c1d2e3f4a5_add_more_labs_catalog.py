"""add more labs to catalogo_labs

Revision ID: b7c1d2e3f4a5
Revises: 696f180ac2cd
Create Date: 2026-01-10 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = "b7c1d2e3f4a5"
down_revision = "696f180ac2cd"
branch_labels = None
depends_on = None


LABS = [
    ("Fructosamina", "umol/L", "Metabolico"),
    ("Insulina", "uIU/mL", "Metabolico"),
    ("Urea", "mg/dL", "Renal"),
    ("Acido urico", "mg/dL", "Renal"),
    ("Colesterol no-HDL", "mg/dL", "Lipidico"),
    ("VLDL", "mg/dL", "Lipidico"),
    ("Fosfatasa alcalina", "U/L", "Hepatico"),
    ("GGT", "U/L", "Hepatico"),
    ("Bilirrubina total", "mg/dL", "Hepatico"),
    ("Hemoglobina", "g/dL", "Hemograma"),
    ("Hematocrito", "%", "Hemograma"),
    ("Leucocitos", "10^3/uL", "Hemograma"),
    ("Plaquetas", "10^3/uL", "Hemograma"),
    ("Sodio", "mmol/L", "Electrolitos"),
    ("Potasio", "mmol/L", "Electrolitos"),
    ("Cloro", "mmol/L", "Electrolitos"),
]


def upgrade() -> None:
    conn = op.get_bind()
    for nombre, unidad, categoria in LABS:
        conn.execute(
            sa.text(
                "insert into public.catalogo_labs (id, nombre, unidad, categoria, activo) "
                "values (:id, :nombre, :unidad, :categoria, true) "
                "on conflict (nombre) do update set "
                "unidad = excluded.unidad, "
                "categoria = excluded.categoria, "
                "activo = true"
            ),
            {
                "id": uuid.uuid4(),
                "nombre": nombre,
                "unidad": unidad,
                "categoria": categoria,
            },
        )


def downgrade() -> None:
    conn = op.get_bind()
    for nombre, _, _ in LABS:
        conn.execute(
            sa.text("delete from public.catalogo_labs where nombre = :nombre"),
            {"nombre": nombre},
        )
