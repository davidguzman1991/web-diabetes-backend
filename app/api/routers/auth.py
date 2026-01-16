from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.models.patient import Patient
from app.models.user import User
from app.schemas.auth import Token, PatientLogin, AdminLogin, PatientToken
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth")
COOKIE_NAME = "access_token"


def _set_auth_cookie(response: Response, token: str, expires_delta: timedelta | None) -> None:
    is_prod = str(settings.ENV).lower() == "production"
    max_age = int(expires_delta.total_seconds()) if expires_delta else None
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=is_prod,
        samesite="none" if is_prod else "lax",
        max_age=max_age,
        path="/",
    )


@router.post("/patient/login", response_model=PatientToken)
def login_patient(
    data: PatientLogin,
    response: Response,
    db: Session = Depends(get_db),
):
    result = (
        db.query(User, Patient)
        .outerjoin(Patient, Patient.cedula == User.username)
        .filter(User.username == data.cedula)
        .first()
    )
    user = result[0] if result else None
    patient = result[1] if result else None
    if not user or user.role.lower() != "patient":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    expires_delta = timedelta(days=7)
    expires_at = datetime.utcnow() + expires_delta
    token = create_access_token({"sub": str(user.id), "role": "PATIENT"}, expires_delta=expires_delta)
    _set_auth_cookie(response, token, expires_delta)
    nombres = patient.nombres if patient else ""
    apellidos = patient.apellidos if patient else ""
    full_name = f"{nombres} {apellidos}".strip()
    return PatientToken(
        access_token=token,
        expires_at=expires_at,
        cedula=patient.cedula if patient else user.username,
        nombres=nombres or "",
        apellidos=apellidos or "",
        full_name=full_name,
    )


@router.post("/admin/login", response_model=Token)
def login_admin(data: AdminLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not user.activo or user.role.lower() != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": str(user.id), "role": "ADMIN"}, expires_delta=expires_delta)
    _set_auth_cookie(response, token, expires_delta)
    return Token(access_token=token)


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"message": "Logged out"}


@router.get("/me", response_model=UserOut)
def get_me(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    cedula = ""
    nombres = ""
    apellidos = ""
    full_name = ""

    if str(current_user.role).lower() == "patient":
        cedula = getattr(current_user, "cedula", "") or getattr(current_user, "username", "") or ""
        patient = None
        if cedula:
            patient = db.query(Patient).filter(Patient.cedula == cedula).first()
        if patient:
            nombres = patient.nombres or ""
            apellidos = patient.apellidos or ""
        full_name = f"{nombres} {apellidos}".strip()

    return UserOut(
        id=str(current_user.id),
        username=current_user.username,
        role=current_user.role,
        activo=bool(current_user.activo),
        cedula=cedula,
        nombres=nombres,
        apellidos=apellidos,
        full_name=full_name,
    )


@router.get("/admin/me", response_model=UserOut)
def get_admin_me(current_user = Depends(get_current_user)) -> UserOut:
    if str(current_user.role).lower() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return UserOut(
        id=str(current_user.id),
        username=current_user.username,
        role=current_user.role,
        activo=bool(current_user.activo),
    )
