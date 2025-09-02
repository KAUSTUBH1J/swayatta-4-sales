from sqlalchemy.orm import Session
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy import or_, func
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.models.user_management.user import User
from app.schemas.user_management.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ================= Helpers =================

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def map_user_with_names(user: User) -> Optional[User]:
    """
    Maps related names to user object (adds extra attributes).
    """
    if not user:
        return None

    user.department_name = user.department.name if user.department else None
    user.sub_department_name = user.sub_department.name if user.sub_department else None
    user.designation_name = user.designation.name if user.designation else None
    user.region_name = user.region.name if user.region else None
    user.role_name = user.role.name if user.role else None
    user.business_vertical_name = (
        user.business_vertical.name if user.business_vertical else None
    )
    user.manager_name = user.manager.full_name if user.manager else None
    user.created_by_name = user.created_user.full_name if user.created_user else None
    user.updated_by_name = user.updated_user.full_name if user.updated_user else None

    return user


# ================= Services =================

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    try:
        return db.query(User).filter(
            User.username == username,
            User.is_deleted == False
        ).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while fetching user by username")


def create_user(db: Session, user_data: UserCreate, login_id: int) -> User:
    try:
        # ===== Duplicate Username Check =====
        existing_username = db.query(User).filter(
            func.lower(User.username) == func.lower(user_data.username)
        ).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{user_data.username}' already exists."
            )

        # ===== Duplicate Email Check =====
        existing_email = db.query(User).filter(
            func.lower(User.email) == func.lower(user_data.email)
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{user_data.email}' is already registered."
            )

        # ===== Insert User =====
        db_user = User(
            full_name=user_data.full_name,
            username=user_data.username,
            email=user_data.email,
            contact_no=user_data.contact_no,
            gender=user_data.gender,
            dob=user_data.dob,
            profile_photo=user_data.profile_photo,
            department_id=user_data.department_id,
            sub_department_id=user_data.sub_department_id,
            designation_id=user_data.designation_id,
            is_reporting=user_data.is_reporting,
            reporting_to=user_data.reporting_to,
            region_id=user_data.region_id,
            role_id=user_data.role_id,
            assign_modules=user_data.assign_modules,
            address=user_data.address,
            business_vertical_id=user_data.business_vertical_id,
            is_active=user_data.is_active,
            created_by=login_id,
            password_hash=get_password_hash(user_data.password),
            is_password_changed=True,
            is_deleted=False
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return map_user_with_names(db_user)

    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while creating user")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong while creating user")


def get_users(db: Session, skip: int = 0, limit: int = 10, search: str = None) -> dict:
    try:
        query = db.query(User).filter(User.is_deleted == False)

        if search:
            query = query.filter(
                or_(
                    User.full_name.ilike(f"%{search}%"),
                    User.username.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.contact_no.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        users = query.order_by(User.id.asc()).offset(skip).limit(limit).all()
        users_data = [map_user_with_names(u) for u in users]

        return {
            "users": users_data,
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while fetching users")
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong while fetching users")


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    try:
        user = db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()
        return map_user_with_names(user) if user else None
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while fetching user by ID")


def update_user(db: Session, user_id: int, user_data: UserUpdate, login_id: int = None) -> Optional[User]:
    try:
        db_user = db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()
        if not db_user:
            return None

        update_data = user_data.dict(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            db_user.password_hash = get_password_hash(update_data.pop("password"))
            db_user.is_password_changed = True

        for field, value in update_data.items():
            setattr(db_user, field, value)

        if login_id:
            db_user.updated_by = login_id

        db.commit()
        db.refresh(db_user)
        return map_user_with_names(db_user)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while updating user")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong while updating user")


def delete_user(db: Session, user_id: int, login_id: int = None) -> Optional[User]:
    try:
        db_user = db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()
        if not db_user:
            return None

        db_user.is_deleted = True
        if login_id:
            db_user.updated_by = login_id

        db.commit()
        db.refresh(db_user)
        return map_user_with_names(db_user)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while deleting user")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong while deleting user")
