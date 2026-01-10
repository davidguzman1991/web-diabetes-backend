"""add consultation_date to consultations

Revision ID: 696f180ac2cd
Revises: a1b2c3d4e5f6
Create Date: 2026-01-09 23:55:35.864639

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '696f180ac2cd'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("consultations", sa.Column("consultation_date", sa.Date(), nullable=True))
    op.create_index(
        op.f("ix_consultations_consultation_date"),
        "consultations",
        ["consultation_date"],
        unique=False,
    )
    op.execute(
        "UPDATE consultations SET consultation_date = DATE(created_at) "
        "WHERE consultation_date IS NULL;"
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_consultations_consultation_date"), table_name="consultations")
    op.drop_column("consultations", "consultation_date")
