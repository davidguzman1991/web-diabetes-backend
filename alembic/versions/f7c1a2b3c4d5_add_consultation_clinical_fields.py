"""add consultation clinical fields

Revision ID: f7c1a2b3c4d5
Revises: e7a1c2d3e4f5
Create Date: 2025-12-27 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f7c1a2b3c4d5"
down_revision = "e7a1c2d3e4f5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("consultations", sa.Column("weight", sa.Float(), nullable=True))
    op.add_column("consultations", sa.Column("height", sa.Float(), nullable=True))
    op.add_column("consultations", sa.Column("blood_pressure", sa.String(length=50), nullable=True))
    op.add_column("consultations", sa.Column("heart_rate", sa.Integer(), nullable=True))
    op.add_column("consultations", sa.Column("oxygen_saturation", sa.Integer(), nullable=True))
    op.add_column("consultations", sa.Column("abdominal_circumference", sa.Float(), nullable=True))
    op.add_column("consultations", sa.Column("reason_for_visit", sa.String(length=255), nullable=True))
    op.add_column("consultations", sa.Column("current_illness", sa.Text(), nullable=True))
    op.add_column("consultations", sa.Column("physical_exam", sa.Text(), nullable=True))
    op.add_column("consultations", sa.Column("requested_exams", sa.Text(), nullable=True))
    op.add_column("consultations", sa.Column("next_visit_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("consultations", "next_visit_date")
    op.drop_column("consultations", "requested_exams")
    op.drop_column("consultations", "physical_exam")
    op.drop_column("consultations", "current_illness")
    op.drop_column("consultations", "reason_for_visit")
    op.drop_column("consultations", "abdominal_circumference")
    op.drop_column("consultations", "oxygen_saturation")
    op.drop_column("consultations", "heart_rate")
    op.drop_column("consultations", "blood_pressure")
    op.drop_column("consultations", "height")
    op.drop_column("consultations", "weight")
