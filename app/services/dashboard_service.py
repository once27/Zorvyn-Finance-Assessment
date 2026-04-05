import time
from decimal import Decimal

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.models.record import FinancialRecord, RecordType

# ── Simple in-memory TTL cache ──────────────────────────────────────────────
_cache: dict = {}
CACHE_TTL = 300  # seconds


def _get(key: str):
    entry = _cache.get(key)
    if entry and time.time() - entry["ts"] < CACHE_TTL:
        return entry["data"]
    return None


def _set(key: str, data):
    _cache[key] = {"data": data, "ts": time.time()}


def invalidate_cache():
    """Call this whenever records are mutated."""
    _cache.clear()


# ── Aggregation queries ──────────────────────────────────────────────────────

def get_summary(db: Session) -> dict:
    if (cached := _get("summary")) is not None:
        return cached

    base = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)  # noqa
    total_income = (
        base.filter(FinancialRecord.type == RecordType.income)
        .with_entities(func.sum(FinancialRecord.amount))
        .scalar() or Decimal("0")
    )
    total_expenses = (
        base.filter(FinancialRecord.type == RecordType.expense)
        .with_entities(func.sum(FinancialRecord.amount))
        .scalar() or Decimal("0")
    )
    result = {
        "total_income": float(total_income),
        "total_expenses": float(total_expenses),
        "net_balance": float(total_income - total_expenses),
    }
    _set("summary", result)
    return result


def get_trends(db: Session) -> list:
    if (cached := _get("trends")) is not None:
        return cached

    rows = (
        db.query(
            extract("year", FinancialRecord.date).label("year"),
            extract("month", FinancialRecord.date).label("month"),
            FinancialRecord.type,
            func.sum(FinancialRecord.amount).label("total"),
        )
        .filter(FinancialRecord.is_deleted == False)  # noqa
        .group_by("year", "month", FinancialRecord.type)
        .order_by("year", "month")
        .all()
    )

    trends: dict = {}
    for row in rows:
        key = f"{int(row.year)}-{int(row.month):02d}"
        if key not in trends:
            trends[key] = {"period": key, "income": 0.0, "expense": 0.0}
        trends[key][row.type.value] = float(row.total)

    result = list(trends.values())
    _set("trends", result)
    return result


def get_category_breakdown(db: Session) -> list:
    if (cached := _get("category_breakdown")) is not None:
        return cached

    rows = (
        db.query(
            FinancialRecord.category,
            FinancialRecord.type,
            func.sum(FinancialRecord.amount).label("total"),
        )
        .filter(FinancialRecord.is_deleted == False)  # noqa
        .group_by(FinancialRecord.category, FinancialRecord.type)
        .all()
    )
    result = [
        {"category": r.category, "type": r.type.value, "total": float(r.total)}
        for r in rows
    ]
    _set("category_breakdown", result)
    return result


def get_recent(db: Session, n: int = 10) -> list:
    records = (
        db.query(FinancialRecord)
        .filter(FinancialRecord.is_deleted == False)  # noqa
        .order_by(FinancialRecord.created_at.desc())
        .limit(n)
        .all()
    )
    return [
        {
            "id": r.id,
            "amount": float(r.amount),
            "type": r.type.value,
            "category": r.category,
            "date": str(r.date),
            "notes": r.notes,
        }
        for r in records
    ]
