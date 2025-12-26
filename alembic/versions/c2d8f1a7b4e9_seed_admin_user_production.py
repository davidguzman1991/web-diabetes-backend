"""seed admin user production

Revision ID: c2d8f1a7b4e9
Revises: 5f78006120ad
Create Date: 2025-12-25 12:45:00.000000

"""
import os
import uuid

from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = "c2d8f1a7b4e9"
down_revision = "5f78006120ad"
branch_labels = None
depends_on = None


def _get_admin_credentials() -> tuple[str, str]:
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    if not username or not password:
        raise RuntimeError("ADMIN_USERNAME and ADMIN_PASSWORD are required to seed admin user")

    from app.core.security import get_password_hash

    return username, get_password_hash(password)


def upgrade() -> None:
    connection = op.get_bind()
    username, password_hash = _get_admin_credentials()
    connection.execute(
        text(
            "INSERT INTO users (id, username, password_hash, role, activo) "
            "VALUES (:id, :username, :password_hash, :role, :activo) "
            "ON CONFLICT (username) DO UPDATE SET "
            "password_hash = EXCLUDED.password_hash, "
            "role = EXCLUDED.role, "
            "activo = EXCLUDED.activo"
        ),
        {
            "id": str(uuid.uuid4()),
            "username": username,
            "password_hash": password_hash,
            "role": "admin",
            "activo": True,
        },
    )
    print("Admin user seeded/updated")


def downgrade() -> None:
    connection = op.get_bind()
    username = os.getenv("ADMIN_USERNAME")
    if not username:
        print("ADMIN_USERNAME not set; skipping admin delete")
        return
    connection.execute(
        text("DELETE FROM users WHERE username = :username"),
        {"username": username},
    )
