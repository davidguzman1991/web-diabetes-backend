"""seed admin user

Revision ID: 983cfc2eb40b
Revises: d55ff8219538
Create Date: 2025-12-21 23:14:11.111877

"""
import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '983cfc2eb40b'
down_revision = 'd55ff8219538'
branch_labels = None
depends_on = None


def _get_admin_credentials() -> tuple[str, str]:
    from app.core.config import settings
    from app.core.security import get_password_hash

    username = settings.ADMIN_USERNAME
    if settings.ADMIN_PASSWORD_HASH:
        password_hash = settings.ADMIN_PASSWORD_HASH
    elif settings.ADMIN_PASSWORD:
        password_hash = get_password_hash(settings.ADMIN_PASSWORD)
    else:
        raise RuntimeError("ADMIN_PASSWORD or ADMIN_PASSWORD_HASH is required to seed admin user")

    return username, password_hash


def upgrade() -> None:
    connection = op.get_bind()
    username, password_hash = _get_admin_credentials()

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
                "role": "admin",
                "activo": True,
            },
        )


def downgrade() -> None:
    connection = op.get_bind()
    from app.core.config import settings
    connection.execute(
        text("DELETE FROM users WHERE username = :username"),
        {"username": settings.ADMIN_USERNAME},
    )
