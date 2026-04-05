from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models.record import RecordType
from app.models.user import Role, User
from app.schemas.record import RecordCreate, RecordRead, RecordUpdate
from app.services import dashboard_service, record_service

router = APIRouter()

admin_dep = Depends(require_roles(Role.admin))


@router.post("", status_code=status.HTTP_201_CREATED)
def create_record(
    payload: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = admin_dep,
):
    record = record_service.create_record(db, payload, current_user.id)
    dashboard_service.invalidate_cache()
    return {"status": "success", "message": "Record created", "data": RecordRead.model_validate(record)}


@router.get("")
def list_records(
    type: Optional[RecordType] = Query(None),
    category: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = record_service.list_records(db, type, category, from_date, to_date, page, limit)
    return {
        "status": "success",
        "data": [RecordRead.model_validate(r) for r in result["items"]],
        "meta": {"total": result["total"], "page": result["page"], "limit": result["limit"]},
    }


@router.get("/{record_id}")
def get_record(
    record_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    record = record_service.get_record_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return {"status": "success", "data": RecordRead.model_validate(record)}


@router.put("/{record_id}")
def update_record(
    record_id: str,
    payload: RecordUpdate,
    db: Session = Depends(get_db),
    _: User = admin_dep,
):
    try:
        record = record_service.update_record(db, record_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    dashboard_service.invalidate_cache()
    return {"status": "success", "message": "Record updated", "data": RecordRead.model_validate(record)}


@router.delete("/{record_id}")
def delete_record(
    record_id: str,
    db: Session = Depends(get_db),
    _: User = admin_dep,
):
    try:
        record_service.soft_delete_record(db, record_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    dashboard_service.invalidate_cache()
    return {"status": "success", "message": "Record deleted successfully"}
