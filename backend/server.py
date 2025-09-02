from fastapi import FastAPI, APIRouter, Form, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
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
                            "permissions": ["view", "create", "edit", "delete"],
                            "children": []
                        },
                        {
                            "id": 102,
                            "name": "Contacts",
                            "path": "/sales/contacts",
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


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

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
        "created_at": "2025-09-02T08:26:02.937087",
        "addresses": [],
        "turnover_records": [],
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
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@acme.com",
        "primary_no": "+1234567890",
        "company_id": 1,
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087",
        "addresses": []
    },
    {
        "id": 2,
        "first_name": "Jane",
        "last_name": "Smith", 
        "email": "jane.smith@beta.com",
        "primary_no": "+9876543210",
        "company_id": 2,
        "is_active": True,
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
