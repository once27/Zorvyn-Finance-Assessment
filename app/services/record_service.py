from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.models.record import FinancialRecord, RecordType
from app.schemas.record import RecordCreate, RecordUpdate


def create_record(db: Session, payload: RecordCreate, user_id: str) -> FinancialRecord:
    record = FinancialRecord(
        user_id=user_id,
        amount=payload.amount,
        type=payload.type,
        category=payload.category,
        date=payload.date,
        notes=payload.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_records(
    db: Session,
    record_type: Optional[RecordType] = None,
    category: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = 1,
    limit: int = 20,
) -> dict:
    query = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)  # noqa: E712

    if record_type:
        query = query.filter(FinancialRecord.type == record_type)
    if category:
        query = query.filter(FinancialRecord.category.ilike(f"%{category}%"))
    if from_date:
        query = query.filter(FinancialRecord.date >= from_date)
    if to_date:
        query = query.filter(FinancialRecord.date <= to_date)

    total = query.count()
    items = (
        query.order_by(FinancialRecord.date.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return {"items": items, "total": total, "page": page, "limit": limit}


def get_record_by_id(db: Session, record_id: str) -> FinancialRecord | None:
    return db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted == False,  # noqa: E712
    ).first()


def update_record(db: Session, record_id: str, payload: RecordUpdate) -> FinancialRecord:
    record = get_record_by_id(db, record_id)
    if not record:
        raise ValueError("Record not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


def soft_delete_record(db: Session, record_id: str) -> None:
    record = get_record_by_id(db, record_id)
    if not record:
        raise ValueError("Record not found")
    record.is_deleted = True
    db.commit()
