from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from typing import Optional, Dict, Any

from app.models.user_management.menu import Menu
from app.schemas.user_management.menu import MenuCreate, MenuUpdate


# ---------------- Map Menu ----------------
def map_menu_with_names(menu: Menu) -> Optional[Dict[str, Any]]:
    if not menu:
        return None
    return {
        "id": menu.id,
        "name": menu.name,
        "path": menu.path,
        "parent_id": menu.parent_id,
        "parent_name": menu.parent_menu.name if menu.parent_menu else None,
        "module_id": menu.module_id,
        "module_name": menu.module.name if menu.module else None,
        "order_index": menu.order_index,
        "icon": menu.icon,
        "is_sidebar": menu.is_sidebar,
        "is_active": menu.is_active,
        "is_deleted": menu.is_deleted,
        "created_by": menu.created_by,
        "updated_by": menu.updated_by,
        "created_at": menu.created_at,
        "updated_at": menu.updated_at,
        "created_by_name": menu.created_user.full_name if menu.created_user else None,
        "updated_by_name": menu.updated_user.full_name if menu.updated_user else None
    }


# ---------------- Create Menu ----------------
def create_menu(db: Session, menu_data: MenuCreate, login_id: int) -> Dict[str, Any]:
    try:
        # Duplicate Name
        existing_name = db.query(Menu).filter(
            func.lower(Menu.name) == menu_data.name.lower(),
            Menu.is_deleted == False
        ).first()
        if existing_name:
            raise HTTPException(status_code=400, detail=f"Menu name '{menu_data.name}' already exists.")

        # Duplicate Path
        if menu_data.path:
            existing_path = db.query(Menu).filter(
                func.lower(Menu.path) == menu_data.path.lower(),
                Menu.is_deleted == False
            ).first()
            if existing_path:
                raise HTTPException(status_code=400, detail=f"Menu path '{menu_data.path}' already exists.")

        # Create Menu
        db_menu = Menu(
            name=menu_data.name,
            path=menu_data.path,
            parent_id=menu_data.parent_id,
            module_id=menu_data.module_id,
            order_index=menu_data.order_index,
            icon=menu_data.icon,
            is_sidebar=menu_data.is_sidebar,
            is_active=menu_data.is_active if menu_data.is_active is not None else True,
            is_deleted=False,
            created_by=login_id
        )
        db.add(db_menu)
        db.commit()
        db.refresh(db_menu)
        return map_menu_with_names(db_menu)

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        print("DB Error (Create Menu):", str(e))
        raise HTTPException(status_code=500, detail="Database error while creating menu")
    except Exception as e:
        db.rollback()
        print("Unexpected Error (Create Menu):", str(e))
        raise HTTPException(status_code=500, detail=f"Error creating menu: {str(e)}")


# ---------------- Get All Menus ----------------
def get_menus(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None) -> Dict[str, Any]:
    try:
        query = db.query(Menu).filter(Menu.is_deleted == False)
        if search:
            query = query.filter(or_(Menu.name.ilike(f"%{search}%")))
        total = query.count()
        menus = query.order_by(Menu.id.asc()).offset(skip).limit(limit).options(
            joinedload(Menu.module), joinedload(Menu.parent_menu)
        ).all()
        return {"menus": [map_menu_with_names(m) for m in menus], "total": total, "limit": limit, "page": (skip // limit) + 1}
    except SQLAlchemyError as e:
        db.rollback()
        print("DB Error (Get Menus):", str(e))
        raise HTTPException(status_code=500, detail="Database error while fetching menus")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching menus: {str(e)}")


# ---------------- Get Menu by ID ----------------
def get_menu_by_id(db: Session, menu_id: int) -> Optional[Dict[str, Any]]:
    try:
        menu = db.query(Menu).filter(
            Menu.id == menu_id,
            Menu.is_deleted == False,
            Menu.is_active == True
        ).options(joinedload(Menu.module), joinedload(Menu.parent_menu)).first()
        return map_menu_with_names(menu)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while fetching menu by ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching menu by ID: {str(e)}")



# ---------------- Get Menus by Module ID ----------------

def get_menus_by_module(
    db: Session,
    module_id: int
) -> Dict[str, Any]:
    try:
        query = db.query(Menu).filter(
            Menu.is_deleted == False,
            Menu.module_id == module_id
        )

        menus = query.order_by(Menu.id.asc()).options(
            joinedload(Menu.module),
            joinedload(Menu.parent_menu)
        ).all()

        return {
            "menus": [map_menu_with_names(m) for m in menus],
            "total": len(menus),
            "module_id": module_id
        }
    except SQLAlchemyError as e:
        db.rollback()
        print("DB Error (Get Menus by Module):", str(e))
        raise HTTPException(status_code=500, detail="Database error while fetching menus by module")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching menus by module: {str(e)}")
















# ---------------- Update Menu ----------------
def update_menu(db: Session, menu_id: int, menu_data: MenuUpdate, login_id: int) -> Optional[Dict[str, Any]]:
    try:
        db_menu = db.query(Menu).filter(Menu.id == menu_id, Menu.is_deleted == False).first()
        if not db_menu:
            return None

        update_data = menu_data.dict(exclude_unset=True)

        # Duplicate name check
        if "name" in update_data:
            existing_name = db.query(Menu).filter(
                func.lower(Menu.name) == update_data["name"].lower(),
                Menu.id != menu_id,
                Menu.is_deleted == False
            ).first()
            if existing_name:
                raise HTTPException(status_code=400, detail=f"Menu name '{update_data['name']}' already exists.")

        # Duplicate path check
        if "path" in update_data and update_data["path"]:
            existing_path = db.query(Menu).filter(
                func.lower(Menu.path) == update_data["path"].lower(),
                Menu.id != menu_id,
                Menu.is_deleted == False
            ).first()
            if existing_path:
                raise HTTPException(status_code=400, detail=f"Menu path '{update_data['path']}' already exists.")

        for field, value in update_data.items():
            setattr(db_menu, field, value)
        db_menu.updated_by = login_id
        db.commit()
        db.refresh(db_menu)
        return map_menu_with_names(db_menu)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while updating menu")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating menu: {str(e)}")


# ---------------- Soft Delete Menu ----------------
def delete_menu(db: Session, menu_id: int, login_id: int) -> Optional[Dict[str, Any]]:
    try:
        db_menu = db.query(Menu).filter(Menu.id == menu_id, Menu.is_deleted == False).first()
        if not db_menu:
            return None
        db_menu.is_deleted = True
        db_menu.updated_by = login_id
        db.commit()
        db.refresh(db_menu)
        return map_menu_with_names(db_menu)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while deleting menu")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting menu: {str(e)}")
