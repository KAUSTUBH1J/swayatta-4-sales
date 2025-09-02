from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, or_
from fastapi import HTTPException
from typing import Optional, Dict, Any

from app.models.masters.master_document_types import DocumentType
from app.schemas.masters.master_document_type import DocumentTypeCreate, DocumentTypeUpdate


# ---------- Mapper ----------
def map_document_type(doc: DocumentType) -> Optional[Dict[str, Any]]:
    if not doc:
        return None
    return {
        "id": doc.document_type_id,
        "document_type_name": doc.document_type_name,
        "description": getattr(doc, "description", None),
        "is_active": doc.is_active,
        "is_deleted": doc.is_deleted,
        "created_at": doc.created_at,
        "updated_at": doc.updated_at,
        "created_by": doc.created_by,
        "updated_by": doc.updated_by,
        "created_by_name": doc.created_user.full_name if doc.created_user else None,
        "updated_by_name": doc.updated_user.full_name if doc.updated_user else None,
    }


# ---------- Create ----------
def create_document_type(db: Session, data: DocumentTypeCreate, login_id: int):
    try:
        existing = db.query(DocumentType).filter(
            func.lower(DocumentType.document_type_name) == data.document_type_name.lower(),
            DocumentType.is_deleted == False
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail=f"DocumentType '{data.document_type_name}' already exists")

        new_doc = DocumentType(
            document_type_name=data.document_type_name.strip(),
            description=data.description,
            is_active=data.is_active,
            is_deleted=False,
            created_by=login_id,
            updated_by=login_id
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        return map_document_type(new_doc)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create document type")


# ---------- List ----------
def get_document_types(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    query = db.query(DocumentType).filter(DocumentType.is_deleted == False)

    if search:
        query = query.filter(or_(
            DocumentType.document_type_name.ilike(f"%{search}%"),
            DocumentType.description.ilike(f"%{search}%")
        ))

    total = query.count()
    records = query.order_by(DocumentType.document_type_id.asc()).offset(skip).limit(limit).all()

    return {
        "document_types": [map_document_type(d) for d in records],
        "total": total,
        "limit": limit,
        "page": (skip // limit) + 1
    }


# ---------- Get By ID ----------
def get_document_type_by_id(db: Session, d_id: int):
    record = db.query(DocumentType).filter(
        DocumentType.document_type_id == d_id,
        DocumentType.is_deleted == False
    ).first()
    return map_document_type(record)


# ---------- Update ----------
def update_document_type(db: Session, d_id: int, data: DocumentTypeUpdate, login_id: int):
    db_obj = db.query(DocumentType).filter(
        DocumentType.document_type_id == d_id,
        DocumentType.is_deleted == False
    ).first()

    if not db_obj:
        return None

    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db_obj.updated_by = login_id
    db.commit()
    db.refresh(db_obj)
    return map_document_type(db_obj)


# ---------- Delete (Soft) ----------
def delete_document_type(db: Session, d_id: int, login_id: int):
    db_obj = db.query(DocumentType).filter(
        DocumentType.document_type_id == d_id,
        DocumentType.is_deleted == False
    ).first()
    if not db_obj:
        return None

    db_obj.is_deleted = True
    db_obj.updated_by = login_id
    db.commit()
    db.refresh(db_obj)
    return map_document_type(db_obj)
