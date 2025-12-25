from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import ALGORITHM
from app.core.database import SessionLocal
from app.models.user import User
from app.models.patient import Patient

security = HTTPBearer(
    auto_error=False,
    description="Enter the token without the Bearer prefix",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_token(credentials: HTTPAuthorizationCredentials | None) -> str:
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return credentials.credentials


def get_current_token(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict:
    token = _get_token(credentials)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


class AuthUser:
    def __init__(self, user_id, username: str, role: str, activo: bool) -> None:
        self.id = user_id
        self.username = username
        self.role = role
        self.activo = activo


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> User | AuthUser:
    payload = get_current_token(credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    role = (payload.get("role") or "").strip().upper()
    if role == "PATIENT":
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            if not user.activo:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
            return user

        patient = db.query(Patient).filter(Patient.id == user_id).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not patient.activo:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
        return AuthUser(patient.id, patient.cedula, "patient", bool(patient.activo))

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user


def require_admin(payload: dict = Depends(get_current_token)) -> dict:
    if payload.get("role") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return payload


def require_patient(payload: dict = Depends(get_current_token)) -> dict:
    if payload.get("role") != "PATIENT":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Patient only")
    return payload
