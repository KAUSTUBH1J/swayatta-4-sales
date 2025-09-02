from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func
from fastapi import HTTPException
from typing import Optional, Dict, Any
from app.models.masters.master_states import MasterStates
from app.schemas.masters.master_state import MasterStateCreate, MasterStateUpdate


# ---------------- Mapper ----------------
def map_state(state: MasterStates) -> Optional[Dict[str, Any]]:
    if not state:
        return None
    return {
        "id": state.id,
        "name": state.name,
        "description": state.description,
        "is_active": state.is_active,
        "is_deleted": state.is_deleted,
        "created_by": state.created_by,
        "updated_by": state.updated_by,
        "created_at": state.created_at,
        "updated_at": state.updated_at,
        "created_by_name": state.created_user.full_name if state.created_user else None,
        "updated_by_name": state.updated_user.full_name if state.updated_user else None
    }


# ---------------- Create ----------------
def create_state(db: Session, s_data: MasterStateCreate, login_id: int):
    try:
        # Duplicate check (case-insensitive, not deleted)
        existing_state = db.query(MasterStates).filter(
            func.lower(MasterStates.name) == s_data.name.lower(),
            MasterStates.is_deleted == False
        ).first()

        if existing_state:
            raise HTTPException(
                status_code=400,
                detail=f"State '{s_data.name}' already exists."
            )

        db_state = MasterStates(
            name=s_data.name.strip(),
            description=s_data.description,
            is_active=s_data.is_active,
            is_deleted=False,
            created_by=login_id,
            updated_by=login_id
        )

        db.add(db_state)
        db.commit()
        db.refresh(db_state)

        return map_state(db_state)

    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        import traceback; print("DB Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Database error while creating State")
    except Exception:
        db.rollback()
        import traceback; print("Unexpected Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Something went wrong while creating State")


# ---------------- Get List ----------------
def get_states(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    try:
        query = db.query(MasterStates).filter(MasterStates.is_deleted == False)

        if search:
            query = query.filter(or_(
                MasterStates.name.ilike(f"%{search}%"),
                MasterStates.description.ilike(f"%{search}%")
            ))

        total = query.count()
        records = query.order_by(MasterStates.id.asc()).offset(skip).limit(limit).all()

        return {
            "master_states": [map_state(s) for s in records],
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch states")


# ---------------- Get by ID ----------------
def get_state_by_id(db: Session, s_id: int):
    try:
        record = db.query(MasterStates).filter(
            MasterStates.id == s_id,
            MasterStates.is_deleted == False
        ).first()
        return map_state(record)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch state")


# ---------------- Update ----------------
def update_state(db: Session, s_id: int, data: MasterStateUpdate, login_id: int):
    try:
        db_obj = db.query(MasterStates).filter(
            MasterStates.id == s_id,
            MasterStates.is_deleted == False
        ).first()
        if not db_obj:
            return None

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_state(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update state")


# ---------------- Delete (Soft) ----------------
def delete_state(db: Session, s_id: int, login_id: int):
    try:
        db_obj = db.query(MasterStates).filter(
            MasterStates.id == s_id,
            MasterStates.is_deleted == False
        ).first()
        if not db_obj:
            return None

        db_obj.is_deleted = True
        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_state(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete state")
