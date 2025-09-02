from fastapi import FastAPI, APIRouter, Form, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Security
security = HTTPBearer()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Authentication data (for testing)
VALID_USERS = {
    "admin": {
        "password": "admin123",
        "user_data": {
            "id": 1,
            "username": "admin",
            "full_name": "Admin User",
            "email": "admin@example.com",
            "role_id": 1,
            "assigned_modules": [1, 2],  # User Management + Sales
            "menus": [
                {
                    "id": 1,
                    "module_id": 1,
                    "name": "USER MANAGEMENT",
                    "is_sidebar": True,
                    "icon": "fas fa-cogs",
                    "order_index": 1,
                    "permissions": ["view", "create", "edit", "delete"],
                    "children": [
                        {
                            "id": 2,
                            "name": "Users",
                            "path": "/users",
                            "permissions": ["view", "create", "edit", "delete"],
                            "children": []
                        }
                    ]
                },
                {
                    "id": 100,
                    "module_id": 2,
                    "name": "SALES",
                    "is_sidebar": True,
                    "icon": "fas fa-chart-line",
                    "order_index": 2,
                    "permissions": ["view", "create", "edit", "delete"],
                    "children": [
                        {
                            "id": 101,
                            "name": "Companies",
                            "path": "/sales/companies",
                            "is_sidebar": True,
                            "permissions": ["view", "create", "edit", "delete"],
                            "children": []
                        },
                        {
                            "id": 102,
                            "name": "Contacts",
                            "path": "/sales/contacts",
                            "is_sidebar": True,
                            "permissions": ["view", "create", "edit", "delete"],
                            "children": []
                        }
                    ]
                }
            ]
        }
    }
}

ACTIVE_TOKENS = {}  # Token storage

# ===== DUMMY DATA FOR ALL MODULES =====

# Users dummy data
USERS_DATA = [
    {
        "id": 1,
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "role_id": 1,
        "department_id": 1,
        "designation_id": 1,
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    },
    {
        "id": 2,
        "username": "manager",
        "full_name": "Manager User",
        "email": "manager@example.com",
        "role_id": 2,
        "department_id": 2,
        "designation_id": 2,
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    },
    {
        "id": 3,
        "username": "employee",
        "full_name": "Employee User",
        "email": "employee@example.com",
        "role_id": 3,
        "department_id": 1,
        "designation_id": 3,
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    }
]

# Roles dummy data
ROLES_DATA = [
    {
        "id": 1,
        "name": "Super Admin",
        "description": "Full system access",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    },
    {
        "id": 2,
        "name": "Manager",
        "description": "Department manager access",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    },
    {
        "id": 3,
        "name": "Employee",
        "description": "Basic employee access",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    }
]

# Permissions dummy data
PERMISSIONS_DATA = [
    {"id": 1, "name": "view", "description": "View records", "is_active": True},
    {"id": 2, "name": "create", "description": "Create records", "is_active": True},
    {"id": 3, "name": "edit", "description": "Edit records", "is_active": True},
    {"id": 4, "name": "delete", "description": "Delete records", "is_active": True},
    {"id": 5, "name": "export", "description": "Export data", "is_active": True}
]

# Departments dummy data
DEPARTMENTS_DATA = [
    {
        "id": 1,
        "name": "Information Technology",
        "description": "IT Department",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    },
    {
        "id": 2,
        "name": "Human Resources",
        "description": "HR Department",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    },
    {
        "id": 3,
        "name": "Sales",
        "description": "Sales Department",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    },
    {
        "id": 4,
        "name": "Marketing",
        "description": "Marketing Department",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    }
]

# Designations dummy data
DESIGNATIONS_DATA = [
    {
        "id": 1,
        "name": "System Administrator",
        "description": "System Admin",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    },
    {
        "id": 2,
        "name": "Department Manager",
        "description": "Manager",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    },
    {
        "id": 3,
        "name": "Senior Developer",
        "description": "Senior Developer",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    },
    {
        "id": 4,
        "name": "Sales Executive",
        "description": "Sales Executive",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    }
]

# Business Verticals dummy data
BUSINESS_VERTICALS_DATA = [
    {
        "id": 1,
        "name": "Technology",
        "description": "Technology services",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    },
    {
        "id": 2,
        "name": "Healthcare",
        "description": "Healthcare services",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    },
    {
        "id": 3,
        "name": "Finance",
        "description": "Financial services",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    }
]

# Regions dummy data
REGIONS_DATA = [
    {
        "id": 1,
        "name": "North America",
        "description": "North American region",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    },
    {
        "id": 2,
        "name": "Europe",
        "description": "European region",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    },
    {
        "id": 3,
        "name": "Asia Pacific",
        "description": "Asia Pacific region",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    },
    {
        "id": 4,
        "name": "India",
        "description": "India region",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087"
    }
]


# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.get("/status")
async def status():
    return {"status": "OK", "message": "Sales API is running", "timestamp": datetime.utcnow().isoformat()}

# ===== AUTHENTICATION ENDPOINTS =====

@api_router.post("/v1/auth/token")
async def login(username: str = Form(...), password: str = Form(...)):
    """Login endpoint"""
    if username not in VALID_USERS or VALID_USERS[username]["password"] != password:
        raise HTTPException(
            status_code=401, 
            detail={
                "status_code": 401,
                "message": "Invalid credentials",
                "data": None
            }
        )
    
    # Generate token
    token = f"token_{username}_{len(ACTIVE_TOKENS) + 1}"
    ACTIVE_TOKENS[token] = VALID_USERS[username]["user_data"]
    
    return {
        "status_code": 200,
        "message": "Login successful",
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "user": VALID_USERS[username]["user_data"]
        }
    }

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    token = credentials.credentials
    if token not in ACTIVE_TOKENS:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return ACTIVE_TOKENS[token]

@api_router.get("/v1/auth/verify-token/")
async def verify_token_endpoint(user_data: dict = Depends(verify_token)):
    """Verify token endpoint"""
    return {
        "status_code": 200,
        "message": "Token Verified Successfully",
        "data": {
            "user": user_data
        }
    }

# ===== USER MANAGEMENT ENDPOINTS =====

@api_router.get("/v1/users/")
async def list_users(user_data: dict = Depends(verify_token)):
    """List users"""
    return {
        "status_code": 200,
        "message": "Users fetched successfully",
        "data": {
            "users": USERS_DATA,
            "total": len(USERS_DATA),
            "page": 1,
            "limit": 10
        }
    }

@api_router.get("/v1/roles/")
async def list_roles(user_data: dict = Depends(verify_token)):
    """List roles"""
    return {
        "status_code": 200,
        "message": "Roles fetched successfully",
        "data": {
            "roles": ROLES_DATA,
            "total": len(ROLES_DATA),
            "page": 1,
            "limit": 10
        }
    }

@api_router.get("/v1/permissions/")
async def list_permissions(user_data: dict = Depends(verify_token)):
    """List permissions"""
    return {
        "status_code": 200,
        "message": "Permissions fetched successfully",
        "data": {
            "permissions": PERMISSIONS_DATA,
            "total": len(PERMISSIONS_DATA),
            "page": 1,
            "limit": 10
        }
    }

@api_router.get("/v1/departments/")
async def list_departments(user_data: dict = Depends(verify_token)):
    """List departments"""
    return {
        "status_code": 200,
        "message": "Departments fetched successfully",
        "data": {
            "departments": DEPARTMENTS_DATA,
            "total": len(DEPARTMENTS_DATA),
            "page": 1,
            "limit": 10
        }
    }

@api_router.get("/v1/designations/")
async def list_designations(user_data: dict = Depends(verify_token)):
    """List designations"""
    return {
        "status_code": 200,
        "message": "Designations fetched successfully",
        "data": {
            "designations": DESIGNATIONS_DATA,
            "total": len(DESIGNATIONS_DATA),
            "page": 1,
            "limit": 10
        }
    }

@api_router.get("/v1/business-verticals/")
async def list_business_verticals(user_data: dict = Depends(verify_token)):
    """List business verticals"""
    return {
        "status_code": 200,
        "message": "Business verticals fetched successfully",
        "data": {
            "business_verticals": BUSINESS_VERTICALS_DATA,
            "total": len(BUSINESS_VERTICALS_DATA),
            "page": 1,
            "limit": 10
        }
    }

@api_router.get("/v1/regions/")
async def list_regions(user_data: dict = Depends(verify_token)):
    """List regions"""
    return {
        "status_code": 200,
        "message": "Regions fetched successfully",
        "data": {
            "regions": REGIONS_DATA,
            "total": len(REGIONS_DATA),
            "page": 1,
            "limit": 10
        }
    }

# Dropdown endpoints for master data
@api_router.get("/v1/dropdowns/roles")
async def get_roles_dropdown(user_data: dict = Depends(verify_token)):
    """Get roles dropdown"""
    return {
        "status_code": 200,
        "message": "Roles dropdown fetched successfully",
        "data": [{"id": role["id"], "name": role["name"]} for role in ROLES_DATA]
    }

@api_router.get("/v1/dropdowns/departments")
async def get_departments_dropdown(user_data: dict = Depends(verify_token)):
    """Get departments dropdown"""
    return {
        "status_code": 200,
        "message": "Departments dropdown fetched successfully",
        "data": [{"id": dept["id"], "name": dept["name"]} for dept in DEPARTMENTS_DATA]
    }

@api_router.get("/v1/dropdowns/designations")
async def get_designations_dropdown(user_data: dict = Depends(verify_token)):
    """Get designations dropdown"""
    return {
        "status_code": 200,
        "message": "Designations dropdown fetched successfully",
        "data": [{"id": desig["id"], "name": desig["name"]} for desig in DESIGNATIONS_DATA]
    }

@api_router.get("/v1/dropdowns/regions")
async def get_regions_dropdown(user_data: dict = Depends(verify_token)):
    """Get regions dropdown"""
    return {
        "status_code": 200,
        "message": "Regions dropdown fetched successfully",
        "data": [{"id": region["id"], "name": region["name"]} for region in REGIONS_DATA]
    }

# ===== SALES ENDPOINTS =====

# Sample data
COMPANIES_DATA = [
    {
        "id": 1,
        "company_name": "Acme Corporation",
        "gst_no": "27AAAAA0000A1Z5",
        "pan_no": "AAAAA0000A",
        "website": "https://acme.com",
        "is_child": False,
        "is_active": True,
        "company_profile": "Leading technology company specializing in innovative solutions",
        "industry_segment_id": 1,
        "account_type_id": 1,
        "account_region_id": 1,
        "created_at": "2025-09-02T08:26:02.937087",
        "addresses": [
            {
                "id": 1,
                "company_id": 1,
                "address": "123 Tech Street, Silicon Valley, CA",
                "zip_code": "94000",
                "is_active": True
            }
        ],
        "turnover_records": [
            {
                "id": 1,
                "company_id": 1,
                "year": 2023,
                "revenue": "10000000.00",
                "currency_id": 1
            }
        ],
        "profit_records": [],
        "documents": []
    },
    {
        "id": 2,
        "company_name": "Beta Industries", 
        "gst_no": "27BBBBB1111B2Y4",
        "pan_no": "BBBBB1111B",
        "website": "https://beta.com",
        "is_child": False,
        "is_active": True,
        "company_profile": "Manufacturing company with 50+ years of experience",
        "industry_segment_id": 2,
        "account_type_id": 1,
        "account_region_id": 2,
        "created_at": "2025-09-02T08:26:02.937087",
        "addresses": [
            {
                "id": 2,
                "company_id": 2,
                "address": "456 Industrial Ave, Detroit, MI",
                "zip_code": "48201",
                "is_active": True
            }
        ],
        "turnover_records": [
            {
                "id": 2,
                "company_id": 2,
                "year": 2023,
                "revenue": "5000000.00",
                "currency_id": 1
            }
        ],
        "profit_records": [],
        "documents": []
    },
    {
        "id": 3,
        "company_name": "Gamma Tech Solutions",
        "gst_no": "27CCCCC2222C3X3",
        "pan_no": "CCCCC2222C",
        "website": "https://gamma.tech",
        "is_child": True,
        "parent_company_id": 1,
        "is_active": True,
        "company_profile": "Subsidiary focusing on AI and machine learning solutions",
        "industry_segment_id": 1,
        "account_type_id": 2,
        "account_region_id": 3,
        "created_at": "2025-09-02T08:26:02.937087",
        "addresses": [],
        "turnover_records": [],
        "profit_records": [],
        "documents": []
    }
]

CONTACTS_DATA = [
    {
        "id": 1,
        "title_id": 1,
        "first_name": "John",
        "middle_name": "A",
        "last_name": "Doe",
        "email": "john.doe@acme.com",
        "primary_no": "+1234567890",
        "secondary_no": "+1234567891",
        "company_id": 1,
        "designation_id": 1,
        "is_active": True,
        "dont_call": False,
        "dont_email": False,
        "dont_mail": False,
        "dont_solicit": False,
        "dont_fax": False,
        "dob": "1985-05-15",
        "created_at": "2025-09-02T08:26:02.937087",
        "addresses": [
            {
                "id": 1,
                "contact_id": 1,
                "address": "123 Main St, Apartment 4B",
                "zip_code": "10001",
                "is_active": True
            }
        ]
    },
    {
        "id": 2,
        "title_id": 2,
        "first_name": "Jane",
        "middle_name": "",
        "last_name": "Smith", 
        "email": "jane.smith@beta.com",
        "primary_no": "+9876543210",
        "secondary_no": "",
        "company_id": 2,
        "designation_id": 2,
        "is_active": True,
        "dont_call": False,
        "dont_email": False,
        "dont_mail": True,
        "dont_solicit": False,
        "dont_fax": True,
        "dob": "1990-08-22",
        "created_at": "2025-09-02T08:26:02.937087",
        "addresses": []
    },
    {
        "id": 3,
        "title_id": 1,
        "first_name": "Michael",
        "middle_name": "R",
        "last_name": "Johnson",
        "email": "michael.johnson@gamma.tech",
        "primary_no": "+1555123456",
        "secondary_no": "+1555123457",
        "company_id": 3,
        "designation_id": 3,
        "is_active": True,
        "dont_call": False,
        "dont_email": False,
        "dont_mail": False,
        "dont_solicit": False,
        "dont_fax": False,
        "dob": "1988-12-10",
        "created_at": "2025-09-02T08:26:02.937087",
        "addresses": []
    }
]

@api_router.get("/v1/sales/companies/")
async def list_companies(user_data: dict = Depends(verify_token)):
    """List companies"""
    return {
        "status_code": 200,
        "message": "Companies fetched successfully",
        "data": {
            "companies": COMPANIES_DATA,
            "total": len(COMPANIES_DATA),
            "page": 1,
            "limit": 10
        }
    }

@api_router.get("/v1/sales/contacts/")
async def list_contacts(user_data: dict = Depends(verify_token)):
    """List contacts"""
    return {
        "status_code": 200,
        "message": "Contacts fetched successfully", 
        "data": {
            "contacts": CONTACTS_DATA,
            "total": len(CONTACTS_DATA),
            "page": 1,
            "limit": 10
        }
    }

@api_router.get("/v1/sales/companies/parent-companies")
async def get_parent_companies(user_data: dict = Depends(verify_token)):
    """Get parent companies dropdown"""
    return {
        "status_code": 200,
        "message": "Parent companies fetched successfully",
        "data": [{"id": c["id"], "name": c["company_name"]} for c in COMPANIES_DATA]
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
