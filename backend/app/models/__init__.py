# Import all models to register them with SQLAlchemy

# User Management Models
from app.models.user_management.user import User
from app.models.user_management.role import Role
from app.models.user_management.permission import Permission
from app.models.user_management.role_permission import RolePermission
from app.models.user_management.user_permission import UserPermission
from app.models.user_management.department import Department
from app.models.user_management.sub_department import SubDepartment
from app.models.user_management.designation import Designation
from app.models.user_management.business_vertical import BusinessVertical
from app.models.user_management.region import Region
from app.models.user_management.menu import Menu
from app.models.user_management.module import Module

# Master Models (using actual class names from files)
from app.models.masters.master_account_types import MasterAccountTypes
from app.models.masters.master_account_sub_types import AccountSubType
from app.models.masters.master_business_types import MasterBusinessTypes
from app.models.masters.master_industry_segment import MasterIndustrySegments
from app.models.masters.master_address_type import MasterAddresssTypes
from app.models.masters.master_countries import MasterCountries
from app.models.masters.master_states import MasterStates
from app.models.masters.master_cities import MasterCities
from app.models.masters.master_document_types import DocumentType
from app.models.masters.master_currency import MasterCurrency
from app.models.masters.master_titles import Title

# Sales Models
from app.models.sales.company import (
    Company, CompanyAddress, CompanyTurnover, 
    CompanyProfit, CompanyDocument
)
from app.models.sales.contact import Contact, ContactAddress
