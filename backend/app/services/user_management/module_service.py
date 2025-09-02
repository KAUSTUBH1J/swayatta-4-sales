from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from fastapi import HTTPException
from sqlalchemy import func
from fastapi import FastAPI,status
from app.models.user_management.module import Module
from app.schemas.user_management.module import ModuleCreate, ModuleOut

# ---------------- Serializer ----------------
def serialize_module(module: Module) -> dict:
    return {
        "id": module.id,
        "name": module.name,
        "description": module.description,
        "is_active": module.is_active,
        "is_deleted": module.is_deleted,
        "created_by": module.created_by,
        "updated_by": module.updated_by,
        "created_at": module.created_at,
        "updated_at": module.updated_at,
    }

# ---------------- Create ----------------
def create_module(db: Session, module_data: ModuleCreate, login_id: int):
    try:
        # Duplicate check (case-insensitive, only non-deleted)
        existing_module = db.query(Module).filter(
            func.lower(Module.name) == module_data.name.lower(),
            Module.is_deleted == False
        ).first()

        if existing_module:
            raise HTTPException(
                status_code=400,
                detail=f"Module '{module_data.name}' already exists."
            )

        # Save exactly as entered
        db_module = Module(
            name=module_data.name.strip(),
            description=module_data.description,
            is_active=module_data.is_active if hasattr(module_data, "is_active") else True,
            is_deleted=False,
            created_by=login_id,
            updated_by=login_id
        )

        db.add(db_module)
        db.commit()
        db.refresh(db_module)

        return serialize_module(db_module)

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        db.rollback()
        print("DB Error (Create Module):", str(e))
        raise HTTPException(status_code=500, detail="Database error occurred while creating module")

    except Exception as e:
        db.rollback()
        print("Unexpected Error (Create Module):", str(e))
        raise HTTPException(status_code=500, detail="Something went wrong while creating module")

# ---------------- Get All ----------------
def get_modules(db: Session, skip: int = 0, limit: int = 50, search: str = None):
    try:
        query = db.query(Module).filter(Module.is_deleted == False, Module.is_active == True)

        if search:
            query = query.filter(
                or_(
                    Module.name.ilike(f"%{search}%"),
                    Module.description.ilike(f"%{search}%")
                )
            )

        total = query.count()
        modules = query.offset(skip).limit(limit).all()
        modules_data = [serialize_module(m) for m in modules]

        return {
            "modules": modules_data,
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while fetching modules")
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong while fetching modules")

# ---------------- Get By ID ----------------
def get_module_by_id(db: Session, module_id: int):
    try:
        module = db.query(Module).filter(
            Module.id == module_id,
            Module.is_deleted == False,
            Module.is_active == True
        ).first()
        return serialize_module(module) if module else None
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while fetching module by ID")

# ---------------- Update ----------------
def update_module(db: Session, module_id: int, module_data: ModuleOut, login_id: int = None):
    try:
        db_module = db.query(Module).filter(
            Module.id == module_id,
            Module.is_deleted == False,
            Module.is_active == True
        ).first()
        if not db_module:
            return None

        update_data = module_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_module, field, value)

        if login_id:
            db_module.updated_by = login_id

        db.commit()
        db.refresh(db_module)
        return serialize_module(db_module)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while updating module")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong while updating module")

# ---------------- Soft Delete ----------------
def delete_module(db: Session, module_id: int, login_id: int = None):
    try:
        db_module = db.query(Module).filter(
            Module.id == module_id,
            Module.is_deleted == False
        ).first()
        if not db_module:
            return None

        db_module.is_deleted = True
        if login_id:
            db_module.updated_by = login_id

        db.commit()
        db.refresh(db_module)
        return serialize_module(db_module)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while deleting module")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong while deleting module")
