"""add labs catalog and consulta labs

Revision ID: 4c8b8f1e0d2a
Revises: 3f2d9b4c2c1e
Create Date: 2025-12-24 02:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = "4c8b8f1e0d2a"
down_revision = "3f2d9b4c2c1e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "catalogo_labs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("nombre", sa.Text(), nullable=False),
        sa.Column("unidad", sa.Text(), nullable=True),
        sa.Column("rango_ref_min", sa.Float(), nullable=True),
        sa.Column("rango_ref_max", sa.Float(), nullable=True),
        sa.Column("activo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre"),
    )
    op.create_index("ix_catalogo_labs_nombre", "catalogo_labs", ["nombre"], unique=False)

    op.create_table(
        "consulta_labs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("consulta_id", sa.UUID(), nullable=False),
        sa.Column("lab_id", sa.UUID(), nullable=False),
        sa.Column("valor_num", sa.Float(), nullable=True),
        sa.Column("valor_texto", sa.Text(), nullable=True),
        sa.Column("unidad_snapshot", sa.Text(), nullable=True),
        sa.Column("rango_ref_snapshot", sa.Text(), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["consulta_id"], ["consultations.id"]),
        sa.ForeignKeyConstraint(["lab_id"], ["catalogo_labs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_consulta_labs_consulta_id", "consulta_labs", ["consulta_id"], unique=False)
    op.create_index("ix_consulta_labs_lab_id", "consulta_labs", ["lab_id"], unique=False)
    op.create_index("ix_consulta_labs_creado_en", "consulta_labs", ["creado_en"], unique=False)

    catalog_table = sa.table(
        "catalogo_labs",
        sa.column("id", sa.UUID()),
        sa.column("nombre", sa.Text()),
        sa.column("unidad", sa.Text()),
        sa.column("rango_ref_min", sa.Float()),
        sa.column("rango_ref_max", sa.Float()),
        sa.column("activo", sa.Boolean()),
    )
    op.bulk_insert(
        catalog_table,
        [
            {"id": uuid.uuid4(), "nombre": "Glucosa ayunas", "unidad": "mg/dL", "activo": True},
            {"id": uuid.uuid4(), "nombre": "HbA1c", "unidad": "%", "activo": True},
            {"id": uuid.uuid4(), "nombre": "Creatinina", "unidad": "mg/dL", "activo": True},
            {"id": uuid.uuid4(), "nombre": "TFG", "unidad": "mL/min/1.73m2", "activo": True},
            {"id": uuid.uuid4(), "nombre": "UACR", "unidad": "mg/g", "activo": True},
            {"id": uuid.uuid4(), "nombre": "Colesterol LDL", "unidad": "mg/dL", "activo": True},
            {"id": uuid.uuid4(), "nombre": "Trigliceridos", "unidad": "mg/dL", "activo": True},
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_consulta_labs_creado_en", table_name="consulta_labs")
    op.drop_index("ix_consulta_labs_lab_id", table_name="consulta_labs")
    op.drop_index("ix_consulta_labs_consulta_id", table_name="consulta_labs")
    op.drop_table("consulta_labs")
    op.drop_index("ix_catalogo_labs_nombre", table_name="catalogo_labs")
    op.drop_table("catalogo_labs")
