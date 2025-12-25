from fastapi import Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.user import User


def _normalize_role(value: str | None) -> str:
    return (value or "").strip().lower()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if _normalize_role(getattr(current_user, "role", None)) != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return current_user


def require_patient(current_user: User = Depends(get_current_user)) -> User:
    if _normalize_role(getattr(current_user, "role", None)) != "patient":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Patient only")
    return current_user
