from typing import List

from app.models.masters.region import Region
from app.schemas.masters.region import RegionExportOut
from app.models.masters.business_vertical import BusinessVertical
from app.schemas.masters.business_vertical import BusinessVerticalExportOut

from app.schemas.user_management.user import UserExportOut
from app.models.user_management.user import User
from app.models.user_management.role import Role
from app.schemas.user_management.role import RoleExportOut
from app.models.user_management.department import Department
from app.schemas.user_management.department import DepartmentExportOut
from app.models.user_management.sub_department import SubDepartment
from app.schemas.user_management.sub_department import SubDepartmentExportOut
from app.models.user_management.designation import Designation
from app.schemas.user_management.designation import DesignationExportOut

def transform_users_for_export(users: List[User]) -> List[UserExportOut]:
    return [
        UserExportOut(
            full_name=user.full_name,
            username=user.username,
            email=user.email,
            contact_no=user.contact_no,
            gender=user.gender,
            dob=user.dob,
            department_name=user.department.name if user.department else None,
            sub_department_name=user.sub_department.name if user.sub_department else None,
            designation_name=user.designation_obj.name if user.designation_obj else None,
            role_name=user.role.name if user.role else None,
            region_name=user.region_obj.name if user.region_obj else None,
            business_vertical_name=user.business_vertical.name if user.business_vertical else None,
            manager_name=user.manager.full_name if user.manager else None,
            created_by_name=user.created_user.full_name if user.created_user else None,
            updated_by_name=user.updated_user.full_name if user.updated_user else None,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        for user in users
    ]


def transform_roles_for_export(roles: List[Role]) -> List[RoleExportOut]:
    return [
        RoleExportOut(
            name=role.name,
            description=role.description,
            is_active=role.is_active,
            created_by_name=role.created_user.full_name if role.created_user else None,
            updated_by_name=role.updated_user.full_name if role.updated_user else None,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )
        for role in roles
    ]
    

def transform_regions_for_export(regions: List[Region]) -> List[RegionExportOut]:
    return [
        RegionExportOut(
            region_name=region.name,
            description=region.description,
            is_active=region.is_active,
            created_by_name=region.created_user.full_name if region.created_user else None,
            updated_by_name=region.updated_user.full_name if region.updated_user else None,
            created_at=region.created_at,
            updated_at=region.updated_at,
        )
        for region in regions
    ]
    
    
def transform_business_verticals_for_export(verticals: List[BusinessVertical]) -> List[BusinessVerticalExportOut]:
    return [
        BusinessVerticalExportOut(
            business_vertical_name=vertical.name,
            description=vertical.description,
            is_active=vertical.is_active,
            created_by_name=vertical.created_user.full_name if vertical.created_user else None,
            updated_by_name=vertical.updated_user.full_name if vertical.updated_user else None,
            created_at=vertical.created_at,
            updated_at=vertical.updated_at,
        )
        for vertical in verticals
    ]
    

def transform_departments_for_export(departments: List[Department]) -> List[DepartmentExportOut]:
    return [
        DepartmentExportOut(
            name=dept.name,
            code=dept.code,
            description=dept.description,
            is_active=dept.is_active,
            created_by_name=dept.created_user.full_name if dept.created_user else None,
            updated_by_name=dept.updated_user.full_name if dept.updated_user else None,
            created_at=dept.created_at,
            updated_at=dept.updated_at,
           
        )
        for dept in departments
    ]
    
def transform_sub_departments_to_export(sub_departments: list) -> list[SubDepartmentExportOut]:
    return [
        SubDepartmentExportOut(
            name=sub.name,
            code=sub.code,
            description=sub.description,
            department_name=sub.department.name if sub.department else None,
            is_active=sub.is_active,
            created_by_name=sub.created_user.full_name if sub.created_user else None,
            updated_by_name=sub.updated_user.full_name if sub.updated_user else None,
            created_at=sub.created_at,
            updated_at=sub.updated_at,
        )
        for sub in sub_departments
    ]
    
def transform_designations_to_export(designations: list) -> list[DesignationExportOut]:
    return [
        DesignationExportOut(
            designation_name=desig.name,
            description=desig.description,
            is_active=desig.is_active,
            created_by_name=desig.created_user.full_name if desig.created_user else None,
            updated_by_name=desig.updated_user.full_name if desig.updated_user else None,
            created_at=desig.created_at,
            updated_at=desig.updated_at,
        )
        for desig in designations
    ]