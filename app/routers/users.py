from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models.user import Role, User
from app.schemas.user import UserRead, UserRoleUpdate, UserStatusUpdate
from app.services import user_service

router = APIRouter()

admin_dep = Depends(require_roles(Role.admin))


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), _: User = admin_dep):
    return user_service.list_users(db)


@router.patch("/{user_id}/status")
def update_status(
    user_id: str,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    _: User = admin_dep,
):
    try:
        user = user_service.update_user_status(db, user_id, payload.is_active)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {
        "status": "success",
        "message": "User status updated",
        "data": UserRead.model_validate(user),
    }


@router.patch("/{user_id}/role")
def update_role(
    user_id: str,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    _: User = admin_dep,
):
    try:
        user = user_service.update_user_role(db, user_id, payload.role)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {
        "status": "success",
        "message": "User role updated",
        "data": UserRead.model_validate(user),
    }
