# Alias imports to standardize master model naming for Sales module

# Account Types
from app.models.masters.master_account_types import MasterAccountTypes as AccountType

# Account Sub Types (already created)
from app.models.masters.master_account_sub_types import AccountSubType

# Business Types
from app.models.masters.master_business_types import MasterBusinessTypes as BusinessType

# Industry Segments  
from app.models.masters.master_industry_segment import MasterIndustrySegments as IndustrySegment

# Regions
from app.models.user_management.region import Region

# Address Types
from app.models.masters.master_address_type import MasterAddresssTypes as AddressType

# Countries
from app.models.masters.master_countries import MasterCountries as Country

# States
from app.models.masters.master_states import MasterStates as State

# Cities
from app.models.masters.master_cities import MasterCities as City

# Document Types
from app.models.masters.master_document_types import DocumentType

# Currency
from app.models.masters.master_currency import MasterCurrency as Currency

# Titles (already created)
from app.models.masters.master_titles import Title

# Designations
from app.models.user_management.designation import Designation

# Users
from app.models.user_management.user import User