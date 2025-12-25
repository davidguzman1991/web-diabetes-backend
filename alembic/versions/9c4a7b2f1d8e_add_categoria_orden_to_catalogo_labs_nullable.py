"""add categoria and orden to catalogo_labs nullable

Revision ID: 9c4a7b2f1d8e
Revises: 8c2f1a7d3b10
Create Date: 2025-12-24 12:30:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "9c4a7b2f1d8e"
down_revision = "8c2f1a7d3b10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "alter table public.catalogo_labs add column if not exists categoria varchar(100) null"
    )
    op.execute(
        "alter table public.catalogo_labs add column if not exists orden integer not null default 0"
    )
    op.execute(
        "alter table public.catalogo_labs add column if not exists activo boolean not null default true"
    )


def downgrade() -> None:
    op.execute("alter table public.catalogo_labs drop column if exists activo")
    op.execute("alter table public.catalogo_labs drop column if exists orden")
    op.execute("alter table public.catalogo_labs drop column if exists categoria")
