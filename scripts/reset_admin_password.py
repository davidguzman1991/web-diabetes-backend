from sqlalchemy import create_engine, text

from app.core.config import settings
from app.core.security import get_password_hash


def main() -> None:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE users SET password_hash = :ph WHERE username = :u"),
            {"ph": get_password_hash("admin123"), "u": "admin"},
        )


if __name__ == "__main__":
    main()
