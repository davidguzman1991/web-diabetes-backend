"""add consultas and medicamentos

Revision ID: 466016ace4a7
Revises: c71af447f275
Create Date: 2025-12-23 21:19:47.037052

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '466016ace4a7'
down_revision = 'c71af447f275'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "consultas",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("patient_user_id", sa.UUID(), nullable=False),
        sa.Column("fecha", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("diagnostico", sa.Text(), nullable=True),
        sa.Column("notas_medicas", sa.Text(), nullable=True),
        sa.Column("indicaciones_generales", sa.Text(), nullable=True),
        sa.Column("created_by_admin_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["patient_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["created_by_admin_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_consultas_patient_user_id", "consultas", ["patient_user_id"], unique=False)
    op.create_index("ix_consultas_created_by_admin_id", "consultas", ["created_by_admin_id"], unique=False)

    op.create_table(
        "medicamentos",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("consulta_id", sa.UUID(), nullable=False),
        sa.Column("nombre", sa.Text(), nullable=False),
        sa.Column("dosis", sa.Text(), nullable=False),
        sa.Column("horario", sa.Text(), nullable=False),
        sa.Column("via", sa.Text(), nullable=False),
        sa.Column("duracion", sa.Text(), nullable=False),
        sa.Column("notas", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["consulta_id"], ["consultas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_medicamentos_consulta_id", "medicamentos", ["consulta_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_medicamentos_consulta_id", table_name="medicamentos")
    op.drop_table("medicamentos")
    op.drop_index("ix_consultas_created_by_admin_id", table_name="consultas")
    op.drop_index("ix_consultas_patient_user_id", table_name="consultas")
    op.drop_table("consultas")
