from pathlib import Path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User


def main() -> None:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    with Session(engine) as session:
        user = session.query(User).filter(User.username == "0999999999").first()
        password_hash = get_password_hash("patient123")
        if user:
            user.password_hash = password_hash
            user.role = "patient"
            user.activo = True
        else:
            user = User(
                username="0999999999",
                password_hash=password_hash,
                role="patient",
                activo=True,
            )
            session.add(user)
        session.commit()


if __name__ == "__main__":
    main()
