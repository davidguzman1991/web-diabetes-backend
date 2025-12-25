"""update medications schema for prescriptions

Revision ID: 3f2d9b4c2c1e
Revises: 1b93f7c2c6b1
Create Date: 2025-12-24 01:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3f2d9b4c2c1e"
down_revision = "1b93f7c2c6b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("medications", "name", new_column_name="drug_name")
    op.alter_column("medications", "schedule", new_column_name="frequency")
    op.alter_column("medications", "notes", new_column_name="indications")

    op.add_column(
        "medications",
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column(
        "medications",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.add_column(
        "medications",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_medications_created_at", "medications", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_medications_created_at", table_name="medications")
    op.drop_column("medications", "updated_at")
    op.drop_column("medications", "created_at")
    op.drop_column("medications", "sort_order")

    op.alter_column("medications", "indications", new_column_name="notes")
    op.alter_column("medications", "frequency", new_column_name="schedule")
    op.alter_column("medications", "drug_name", new_column_name="name")
