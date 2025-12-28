"""add diagnoses catalog and medication id

Revision ID: d2f3a4b5c6d7
Revises: 5f78006120ad
Create Date: 2025-12-27 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d2f3a4b5c6d7"
down_revision = "5f78006120ad"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "diagnoses_catalog",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("cie10_code", sa.String(length=50), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_diagnoses_catalog_name", "diagnoses_catalog", ["name"], unique=False)

    op.add_column("medications", sa.Column("medication_id", sa.UUID(), nullable=True))
    op.create_index("ix_medications_medication_id", "medications", ["medication_id"], unique=False)
    op.create_foreign_key(
        "fk_medications_medication_id_medication_catalog",
        "medications",
        "medication_catalog",
        ["medication_id"],
        ["id"],
    )

    op.create_index(
        "ix_medication_catalog_nombre_generico",
        "medication_catalog",
        ["nombre_generico"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_medication_catalog_nombre_generico", table_name="medication_catalog")

    op.drop_constraint(
        "fk_medications_medication_id_medication_catalog",
        "medications",
        type_="foreignkey",
    )
    op.drop_index("ix_medications_medication_id", table_name="medications")
    op.drop_column("medications", "medication_id")

    op.drop_index("ix_diagnoses_catalog_name", table_name="diagnoses_catalog")
    op.drop_table("diagnoses_catalog")
