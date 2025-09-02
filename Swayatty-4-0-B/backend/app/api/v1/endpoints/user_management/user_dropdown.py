from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
from enum import Enum
from app.database.db import get_db
from sqlalchemy import asc
from app.models.user_management import (Role, Department, 
    SubDepartment,
    Designation,
    RolePermission,
    Permission,
    Module,
    User,
    Menu
)

from app.models.masters import (
    Region,
    BusinessVertical
)

router = APIRouter()

# Enum for allowed dropdown types
class DropdownType(str, Enum):
    roles = "roles"
    departments = "departments"
    sub_departments = "sub_departments"
    regions = "regions"
    business_verticals = "business_verticals"
    designations = "designations"
    role_permissions = "role_permissions"
    permissions = "permissions"
    module = "module"
    user = "user"
    menu = "menu"

# Mapping Enum values to models with value field & label field (+ optional extra field)
ENTITY_MODELS: Dict[DropdownType, Tuple[type, str, str, str | None]] = {
    DropdownType.roles: (Role, "id", "name", None),
    DropdownType.departments: (Department, "id", "name", None),
    DropdownType.sub_departments: (SubDepartment, "id", "name", "department_id"),
    DropdownType.regions: (Region, "id", "name", None),
    DropdownType.business_verticals: (BusinessVertical, "id", "name", None),
    DropdownType.designations: (Designation, "id", "name", None),
    DropdownType.role_permissions: (RolePermission, "id", "role_id", None),
    DropdownType.permissions: (Permission, "id", "name", None),
    DropdownType.module: (Module, "id", "name", None),
    DropdownType.user: (User, "id", "full_name", None),
    DropdownType.menu: (Menu, "id", "name", "module_id"),
}

@router.get("/{entity_name}", response_model=List[Dict])
def get_dropdown(entity_name: DropdownType, db: Session = Depends(get_db)):
    try:
        if entity_name not in ENTITY_MODELS:
            raise HTTPException(status_code=404, detail=f"Entity '{entity_name}' not found.")

        model, value_field, label_field, extra_field = ENTITY_MODELS[entity_name]

        if not hasattr(model, label_field):
            raise HTTPException(status_code=400, detail=f"Label field '{label_field}' not found in '{entity_name}' model.")

        query = db.query(model)
        if hasattr(model, "is_active"):
            query = query.filter(model.is_active == True)

        records = query.order_by(asc(getattr(model, label_field))).all()

        dropdown_data = []
        for record in records:
            item = {
                "id": getattr(record, value_field),
                "name": getattr(record, label_field),
            }
            if extra_field and hasattr(record, extra_field):
                item[extra_field] = getattr(record, extra_field)
            dropdown_data.append(item)

        return dropdown_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

