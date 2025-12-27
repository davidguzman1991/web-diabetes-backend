from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.security import verify_password, create_access_token
from app.crud import patients as patient_crud
from app.models.user import User
from app.schemas.auth import Token, PatientLogin, AdminLogin
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth")


@router.post("/patient/login", response_model=Token)
def login_patient(data: PatientLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.cedula).first()
    if user and user.role.lower() == "patient":
        if not user.activo:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
        if not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        token = create_access_token({"sub": str(user.id), "role": "PATIENT"})
        return Token(access_token=token)

    patient = patient_crud.get_by_cedula(db, data.cedula)
    if not patient or not patient.activo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(data.password, patient.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": str(patient.id), "role": "PATIENT"})
    return Token(access_token=token)


@router.post("/admin/login", response_model=Token)
def login_admin(data: AdminLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not user.activo or user.role.lower() != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "role": "ADMIN"})
    return Token(access_token=token)


@router.post("/logout")
def logout():
    return {"message": "Logged out"}


@router.get("/me", response_model=UserOut)
def get_me(current_user = Depends(get_current_user)) -> UserOut:
    return UserOut(
        id=str(current_user.id),
        username=current_user.username,
        role=current_user.role,
        activo=bool(current_user.activo),
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
