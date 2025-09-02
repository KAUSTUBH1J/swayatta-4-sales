# models/__init__.py
from .user import User
from .role import Role
from .permission import Permission
from .role_permission import RolePermission
from .user_permission import UserPermission
from .menu import Menu
from .module import Module
from .department import Department
from .sub_department import SubDepartment
from .designation import Designation

__all__ = [
    "User", "Role", "Permission", "RolePermission", "UserPermission",
    "Menu", "Module", "Department", "SubDepartment",
    "Designation", "sub_department"
]
