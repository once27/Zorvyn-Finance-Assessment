from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models.user import Role, User
from app.services import dashboard_service

router = APIRouter()

analyst_dep = Depends(require_roles(Role.analyst, Role.admin))


@router.get("/summary")
def summary(db: Session = Depends(get_db), _: User = analyst_dep):
    return {"status": "success", "data": dashboard_service.get_summary(db)}


@router.get("/trends")
def trends(db: Session = Depends(get_db), _: User = analyst_dep):
    return {"status": "success", "data": dashboard_service.get_trends(db)}


@router.get("/category-breakdown")
def category_breakdown(db: Session = Depends(get_db), _: User = analyst_dep):
    return {"status": "success", "data": dashboard_service.get_category_breakdown(db)}


@router.get("/recent")
def recent(
    n: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return {"status": "success", "data": dashboard_service.get_recent(db, n)}
