from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from fastapi import HTTPException
from typing import Optional, Dict, Any

from app.models.masters.master_currency import MasterCurrency
from app.schemas.masters.master_currency import MasterCurrencyCreate, MasterCurrencyUpdate


# ---------- Mapper ----------
def map_currency(c: MasterCurrency) -> Optional[Dict[str, Any]]:
    if not c:
        return None
    return {
        "currency_id": c.currency_id,
        "currency_code": c.currency_code,
        "currency_name": c.currency_name,
        "symbol": c.symbol,
        "is_active": c.is_active,
        "is_deleted": c.is_deleted,
        "created_at": c.created_at,
        "updated_at": c.updated_at,
        "created_by": c.created_by,
        "updated_by": c.updated_by,
        "created_by_name": c.created_user.full_name if c.created_user else None,
        "updated_by_name": c.updated_user.full_name if c.updated_user else None,
    }


# ---------- Create ----------
def create_currency(db: Session, data: MasterCurrencyCreate, login_id: int):
    existing = db.query(MasterCurrency).filter(
        func.lower(MasterCurrency.currency_code) == data.currency_code.lower(),
        MasterCurrency.is_deleted == False
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail=f"Currency code '{data.currency_code}' already exists")

    new_currency = MasterCurrency(
        currency_code=data.currency_code.strip(),
        currency_name=data.currency_name.strip(),
        symbol=data.symbol,
        is_active=data.is_active,
        is_deleted=False,
        created_by=login_id,
        updated_by=login_id
    )
    db.add(new_currency)
    db.commit()
    db.refresh(new_currency)
    return map_currency(new_currency)


# ---------- List ----------
def get_currencies(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    query = db.query(MasterCurrency).filter(MasterCurrency.is_deleted == False)

    if search:
        query = query.filter(or_(
            MasterCurrency.currency_code.ilike(f"%{search}%"),
            MasterCurrency.currency_name.ilike(f"%{search}%")
        ))

    total = query.count()
    records = query.order_by(MasterCurrency.currency_id.asc()).offset(skip).limit(limit).all()

    return {
        "currencies": [map_currency(c) for c in records],
        "total": total,
        "limit": limit,
        "page": (skip // limit) + 1
    }


# ---------- Get By ID ----------
def get_currency_by_id(db: Session, c_id: int):
    record = db.query(MasterCurrency).filter(
        MasterCurrency.currency_id == c_id,
        MasterCurrency.is_deleted == False
    ).first()
    return map_currency(record)


# ---------- Update ----------
def update_currency(db: Session, c_id: int, data: MasterCurrencyUpdate, login_id: int):
    db_obj = db.query(MasterCurrency).filter(
        MasterCurrency.currency_id == c_id,
        MasterCurrency.is_deleted == False
    ).first()

    if not db_obj:
        return None

    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db_obj.updated_by = login_id
    db.commit()
    db.refresh(db_obj)
    return map_currency(db_obj)


# ---------- Delete (Soft) ----------
def delete_currency(db: Session, c_id: int, login_id: int):
    db_obj = db.query(MasterCurrency).filter(
        MasterCurrency.currency_id == c_id,
        MasterCurrency.is_deleted == False
    ).first()
    if not db_obj:
        return None

    db_obj.is_deleted = True
    db_obj.updated_by = login_id
    db.commit()
    db.refresh(db_obj)
    return map_currency(db_obj)
