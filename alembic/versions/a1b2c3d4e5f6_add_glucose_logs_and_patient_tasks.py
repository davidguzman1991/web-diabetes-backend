"""add glucose logs and patient tasks

Revision ID: a1b2c3d4e5f6
Revises: f7c1a2b3c4d5
Create Date: 2025-12-27 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "f7c1a2b3c4d5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "glucose_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("taken_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_glucose_logs_patient_id", "glucose_logs", ["patient_id"], unique=False)
    op.create_index("ix_glucose_logs_taken_at", "glucose_logs", ["taken_at"], unique=False)

    op.create_table(
        "patient_tasks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_patient_tasks_patient_id", "patient_tasks", ["patient_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_patient_tasks_patient_id", table_name="patient_tasks")
    op.drop_table("patient_tasks")
    op.drop_index("ix_glucose_logs_taken_at", table_name="glucose_logs")
    op.drop_index("ix_glucose_logs_patient_id", table_name="glucose_logs")
    op.drop_table("glucose_logs")
