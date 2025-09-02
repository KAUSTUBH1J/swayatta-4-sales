from fastapi import APIRouter
from app.api.v1.endpoints.user_management import user
from app.api.v1.endpoints.user_management import role
from app.api.v1.endpoints.user_management import menu
from app.api.v1.endpoints.user_management import permission
from app.api.v1.endpoints.user_management import role_permission
from app.api.v1.endpoints.user_management import user_permission
from app.api.v1.endpoints.user_management import department
from app.api.v1.endpoints.user_management import sub_department
from app.api.v1.endpoints.user_management import designation
from app.api.v1.endpoints.user_management import user_dropdown


from app.api.v1.endpoints.masters import business_vertical
from app.api.v1.endpoints.masters import region
from app.api.v1.endpoints.masters import company_type
from app.api.v1.endpoints.masters import head_of_company
from app.api.v1.endpoints.masters import job_function
from app.api.v1.endpoints.masters import partner_type
from app.api.v1.endpoints.masters import product_service_interest
from app.api.v1.endpoints.masters import master_account_type
from app.api.v1.endpoints.masters import master_business_type
from app.api.v1.endpoints.masters import master_industry_segment
from app.api.v1.endpoints.masters import master_sub_industry_segment
from app.api.v1.endpoints.masters import master_address_type
from app.api.v1.endpoints.masters import master_countries
from app.api.v1.endpoints.masters import master_state
from app.api.v1.endpoints.masters import master_cities
from app.api.v1.endpoints.masters import master_document_type
from app.api.v1.endpoints.masters import master_currency
# Sales endpoints
from app.api.v1.endpoints.sales import company
from app.api.v1.endpoints.sales import contact

from app.core import auth

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])

api_router.include_router(user.router, prefix="/users", tags=["Users"])
api_router.include_router(role.router, prefix="/roles", tags=["Roles"])
api_router.include_router(menu.router, prefix="/menus", tags=["Menus"])
api_router.include_router(permission.router, prefix="/permissions", tags=["Permissions"])
api_router.include_router(role_permission.router, prefix="/role_permissions", tags=["Role-Permission"])
api_router.include_router(user_permission.router, prefix="/user_permissions", tags=["User-Permission"])
api_router.include_router(department.router, prefix="/departments", tags=["Department"])
api_router.include_router(sub_department.router, prefix="/sub-departments", tags=["SubDepartment"])
api_router.include_router(designation.router, prefix="/designations", tags=["Designation"])
api_router.include_router(business_vertical.router, prefix="/business_verticals", tags=["Business-Vertical"])
api_router.include_router(region.router, prefix="/regions", tags=["Region"])
api_router.include_router(user_dropdown.router, prefix="/user_dropdowns", tags=["dropdown"])
api_router.include_router(company_type.router, prefix="/company_types", tags=["Company Type"])
api_router.include_router(head_of_company.router, prefix="/head_companies", tags=["Head Of Company"])
api_router.include_router(job_function.router, prefix="/job_functions",tags=["Job Functions"])
api_router.include_router(partner_type.router, prefix="/partner_types",tags=["Partner Type"])
api_router.include_router(product_service_interest.router, prefix="/product_service_interests",tags=["Product Service Interest"])
api_router.include_router(master_account_type.router, prefix="/account_types",tags=["Account Type"])
api_router.include_router(master_business_type.router, prefix="/business_types",tags=["Business Type"])
api_router.include_router(master_industry_segment.router, prefix="/industry_segments", tags=["Industry Segments"])
api_router.include_router(master_sub_industry_segment.router, prefix="/sub_industry_segments", tags=["Sub Industry Segments"])
api_router.include_router(master_address_type.router, prefix="/address_types", tags=["Address Type"])
api_router.include_router(master_countries.router, prefix="/countries", tags=["Countries"])
api_router.include_router(master_state.router, prefix="/states", tags=["State"])
api_router.include_router(master_cities.router, prefix="/cities", tags=["City"])
api_router.include_router(master_cities.router, prefix="/document_types", tags=["Document"])
api_router.include_router(master_currency.router, prefix="/currencies", tags=["Currency"])

# Sales module routes
api_router.include_router(company.router, prefix="/sales/companies", tags=["Companies"])
api_router.include_router(contact.router, prefix="/sales/contacts", tags=["Contacts"])



# from fastapi import APIRouter
# from app.core import auth
# from app.api.v1.endpoints.user_management import (
#     user,
#     role,
#     menu,
#     permission,
#     role_permission,
#     department,
#     sub_department,
#     designation,
#     business_vertical,
#     region
# )

# api_router = APIRouter(prefix="/api/v1")

# #  Auth
# api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])

# # 👥 User Management Endpoints (Grouped)
# endpoints = [
#     (user.router, "/users", "Users"),
#     (role.router, "/roles", "Roles"),
#     (menu.router, "/menus", "Menus"),
#     (permission.router, "/permissions", "Permissions"),
#     (role_permission.router, "/role_permission", "Role-Permission"),
#     (department.router, "/department", "Department"),
#     (sub_department.router, "/sub-department", "SubDepartment"),
#     (designation.router, "/designation", "Designation"),
#     (business_vertical.router, "/business_vertical", "Business-Vertical"),
#     (region.router, "/region", "Region"),
# ]

# for router, prefix, tag in endpoints:
#     api_router.include_router(router, prefix=prefix, tags=[tag])
