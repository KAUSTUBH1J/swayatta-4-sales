from datetime import datetime
from typing import Optional, List, Union

from pydantic import BaseModel, Field
from .DefaultResponse import DefaultResponse


# ---------------- Base Schema ----------------
class RolePermissionBase(BaseModel):
    role_id: int
    module_id: int
    menu_id: int
    permission_ids: str = Field(
        ..., description="Comma separated permission IDs, e.g. '1,2,3'"
    )
    is_active: Optional[bool] = Field(default=True)


# ---------------- Create & Update ----------------
class RolePermissionCreate(RolePermissionBase):
    """Schema for creating RolePermission"""
    pass


class RolePermissionUpdate(RolePermissionBase):
    """Schema for updating RolePermission"""
    pass


# ---------------- Output Schema ----------------
class RolePermissionOut(BaseModel):
    id: int

    role_name: Optional[str] = None
    module_name: Optional[str] = None
    menu_name: Optional[str] = None
    permission_names: List[str] = Field(default_factory=list)

    is_deleted: Optional[bool] = Field(default=False)

    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ---------------- Paginated List ----------------
class PaginatedRolePermissions(BaseModel):
    role_permissions: List[RolePermissionOut]
    total: int
    limit: int
    page: int

    class Config:
        orm_mode = True


# ---------------- Export Schema ----------------
class RolePermissionExportOut(BaseModel):
    role_name: Optional[str] = None
    module_name: Optional[str] = None
    menu_name: Optional[str] = None
    permission_names: List[str] = Field(default_factory=list)

    is_active: Optional[bool] = Field(default=True)
    is_deleted: Optional[bool] = Field(default=False)

    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ---------------- Multiple Create ----------------
class MultiRolePermissionCreate(BaseModel):
    """Schema for bulk role permission create"""
    role_permissions: List[RolePermissionCreate]


# ---------------- API Response ----------------
class RolePermissionResponse(DefaultResponse):
    data: Optional[
        Union[
            RolePermissionOut,
            PaginatedRolePermissions,
            List[RolePermissionExportOut],
        ]
    ] = None



# ---------------- Menu Schema ----------------
class NestedMenuOut(BaseModel):
    rp_id: int
    menu_name: str = Field(..., alias="menu_name")
    menu_permissions: List[str] = Field(..., alias="menu_permissions")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

# ---------------- Module Schema ----------------
class NestedModuleOut(BaseModel):
    module_name: str = Field(..., alias="module_name")
    module_menus: List[NestedMenuOut] = Field(..., alias="module_menus")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

# ---------------- Role Schema ----------------
class NestedRoleOut(BaseModel):
    role_name: str = Field(..., alias="role_name")
    role_modules: List[NestedModuleOut] = Field(..., alias="role_modules")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

# ---------------- Paginated Roles ----------------
class NestedPaginatedRolesOut(BaseModel):
    data_roles: List[NestedRoleOut] = Field(..., alias="data_roles")
    total: int
    limit: int
    page: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

# ---------------- API Response ----------------
class NestedRolePermissionResponse(DefaultResponse):
    data: Optional[Union[NestedRoleOut, NestedPaginatedRolesOut]] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True