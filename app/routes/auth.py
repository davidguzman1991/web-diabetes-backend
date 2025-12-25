from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserLogin, UserOut

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = db.query(User).filter(User.username == data.identifier).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "role": user.role.upper()})
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def get_me(current_user = Depends(get_current_user)) -> UserOut:
    return UserOut(
        id=str(current_user.id),
        username=current_user.username,
        role=current_user.role,
        activo=bool(current_user.activo),
    )
