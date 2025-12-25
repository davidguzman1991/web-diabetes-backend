"""seed patient user if missing

Revision ID: c71af447f275
Revises: b8d33cad2a3c
Create Date: 2025-12-22 23:17:27.193705

"""
import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'c71af447f275'
down_revision = 'b8d33cad2a3c'
branch_labels = None
depends_on = None


def _get_patient_credentials() -> tuple[str, str]:
    from app.core.security import get_password_hash

    username = "0999999999"
    password_hash = get_password_hash("patient123")
    return username, password_hash


def upgrade() -> None:
    connection = op.get_bind()
    username, password_hash = _get_patient_credentials()

    exists = connection.execute(
        text("SELECT 1 FROM users WHERE username = :username"),
        {"username": username},
    ).first()
    if not exists:
        connection.execute(
            text(
                "INSERT INTO users (id, username, password_hash, role, activo) "
                "VALUES (:id, :username, :password_hash, :role, :activo)"
            ),
            {
                "id": str(uuid.uuid4()),
                "username": username,
                "password_hash": password_hash,
                "role": "patient",
                "activo": True,
            },
        )


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(
        text("DELETE FROM users WHERE username = :username"),
        {"username": "0999999999"},
    )
