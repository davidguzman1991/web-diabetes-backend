"""add consultations and medications

Revision ID: 1b93f7c2c6b1
Revises: 466016ace4a7
Create Date: 2025-12-23 23:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1b93f7c2c6b1"
down_revision = "466016ace4a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "consultations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("diagnosis", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("indications", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_consultations_patient_id", "consultations", ["patient_id"], unique=False)
    op.create_index("ix_consultations_created_at", "consultations", ["created_at"], unique=False)

    op.create_table(
        "medications",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("consultation_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("dose", sa.Text(), nullable=True),
        sa.Column("schedule", sa.Text(), nullable=True),
        sa.Column("route", sa.Text(), nullable=True),
        sa.Column("duration", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["consultation_id"], ["consultations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_medications_consultation_id", "medications", ["consultation_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_medications_consultation_id", table_name="medications")
    op.drop_table("medications")
    op.drop_index("ix_consultations_created_at", table_name="consultations")
    op.drop_index("ix_consultations_patient_id", table_name="consultations")
    op.drop_table("consultations")
