#!/usr/bin/env python3
"""
Simple Sales API Server for Testing
Uses in-memory data to simulate the Sales API endpoints with Authentication
"""

from fastapi import FastAPI, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json

app = FastAPI(title="Simple Sales API for Testing")
security = HTTPBearer()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple authentication - in production this would be proper JWT
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

ACTIVE_TOKENS = {}  # In production, use proper JWT

# Simple in-memory data (same as before)
companies_data = [
    {
        "id": 1,
        "company_name": "Acme Corporation",
        "gst_no": "27AAAAA0000A1Z5",
        "pan_no": "AAAAA0000A",
        "website": "https://acme.com",
        "is_child": False,
        "parent_company_id": None,
        "company_profile": "Leading technology company",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087",
        "updated_at": "2025-09-02T08:26:02.937087",
        "addresses": [
            {
                "id": 1,
                "company_id": 1,
                "address": "123 Tech Street, Silicon Valley",
                "zip_code": "94000",
                "is_active": True,
                "created_at": "2025-09-02T08:26:02.937087",
                "updated_at": "2025-09-02T08:26:02.937087"
            }
        ],
        "turnover_records": [
            {
                "id": 1,
                "company_id": 1,
                "year": 2023,
                "revenue": "10000000.00",
                "is_active": True,
                "created_at": "2025-09-02T08:26:02.937087",
                "updated_at": "2025-09-02T08:26:02.937087"
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
        "parent_company_id": None,
        "company_profile": "Manufacturing company",
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087",
        "updated_at": "2025-09-02T08:26:02.937087",
        "addresses": [
            {
                "id": 2,
                "company_id": 2,
                "address": "456 Industrial Ave, Detroit",
                "zip_code": "48201",
                "is_active": True,
                "created_at": "2025-09-02T08:26:02.937087",
                "updated_at": "2025-09-02T08:26:02.937087"
            }
        ],
        "turnover_records": [
            {
                "id": 2,
                "company_id": 2,
                "year": 2023,
                "revenue": "5000000.00",
                "is_active": True,
                "created_at": "2025-09-02T08:26:02.937087",
                "updated_at": "2025-09-02T08:26:02.937087"
            }
        ],
        "profit_records": [],
        "documents": []
    }
]

contacts_data = [
    {
        "id": 1,
        "first_name": "John",
        "middle_name": "",
        "last_name": "Doe",
        "email": "john.doe@acme.com",
        "primary_no": "+1234567890",
        "company_id": 1,
        "is_active": True,
        "dont_call": False,
        "dont_email": False,
        "dont_mail": False,
        "dont_solicit": False,
        "dont_fax": False,
        "created_at": "2025-09-02T08:26:02.937087",
        "updated_at": "2025-09-02T08:26:02.937087",
        "addresses": []
    },
    {
        "id": 2,
        "first_name": "Jane",
        "middle_name": "",
        "last_name": "Smith",
        "email": "jane.smith@beta.com",
        "primary_no": "+9876543210",
        "company_id": 2,
        "is_active": True,
        "dont_call": False,
        "dont_email": False,
        "dont_mail": False,
        "dont_solicit": False,
        "dont_fax": False,
        "created_at": "2025-09-02T08:26:02.937087",
        "updated_at": "2025-09-02T08:26:02.937087",
        "addresses": []
    }
]

# Response models
class SalesResponse(BaseModel):
    status_code: int
    message: str
    data: Optional[dict] = None

# Authentication functions
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token not in ACTIVE_TOKENS:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return ACTIVE_TOKENS[token]

# Root endpoints
@app.get("/")
async def root():
    return {"message": "Simple Sales API Test Server with Authentication", "status": "running"}

@app.get("/api/v1/")
async def api_root():
    return {"message": "Sales API v1", "endpoints": ["/auth/token", "/auth/verify-token", "/sales/companies", "/sales/contacts"]}

# ===== AUTHENTICATION ENDPOINTS =====

@app.post("/api/v1/auth/token")
async def login(username: str = Form(...), password: str = Form(...)):
    """Login endpoint - matches frontend expectations"""
    if username not in VALID_USERS or VALID_USERS[username]["password"] != password:
        raise HTTPException(
            status_code=401, 
            detail={
                "status_code": 401,
                "message": "Invalid credentials",
                "data": None
            }
        )
    
    # Generate a simple token (in production, use proper JWT)
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

@app.get("/api/v1/auth/verify-token/")
async def verify_token_endpoint(user_data: dict = Depends(verify_token)):
    """Verify token endpoint - returns user info with menus"""
    return {
        "status_code": 200,
        "message": "Token Verified Successfully",
        "data": {
            "user": user_data
        }
    }

# ===== SALES ENDPOINTS (Protected) =====

@app.get("/api/v1/sales/companies/")
async def list_companies(
    page: int = 1, 
    limit: int = 10, 
    search: str = None,
    user_data: dict = Depends(verify_token)
):
    filtered_companies = companies_data
    if search:
        filtered_companies = [c for c in companies_data if search.lower() in c['company_name'].lower()]
    
    return {
        "status_code": 200,
        "message": "Companies fetched successfully",
        "data": {
            "companies": filtered_companies,
            "total": len(filtered_companies),
            "page": page,
            "limit": limit
        }
    }

@app.get("/api/v1/sales/companies/{company_id}")
async def get_company(company_id: int, user_data: dict = Depends(verify_token)):
    company = next((c for c in companies_data if c['id'] == company_id), None)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return {
        "status_code": 200,
        "message": "Company fetched successfully",
        "data": company
    }

@app.post("/api/v1/sales/companies/")
async def create_company(company_data: dict, user_data: dict = Depends(verify_token)):
    new_id = max([c['id'] for c in companies_data]) + 1 if companies_data else 1
    new_company = {
        "id": new_id,
        **company_data,
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087",
        "updated_at": "2025-09-02T08:26:02.937087"
    }
    companies_data.append(new_company)
    
    return {
        "status_code": 201,
        "message": "Company created successfully",
        "data": new_company
    }

@app.get("/api/v1/sales/companies/parent-companies")
async def get_parent_companies(user_data: dict = Depends(verify_token)):
    parent_companies = [{"id": c['id'], "name": c['company_name']} for c in companies_data]
    return {
        "status_code": 200,
        "message": "Parent companies fetched successfully",
        "data": parent_companies
    }

# Contacts endpoints (Protected)
@app.get("/api/v1/sales/contacts/")
async def list_contacts(
    page: int = 1, 
    limit: int = 10, 
    search: str = None, 
    company_id: int = None,
    user_data: dict = Depends(verify_token)
):
    filtered_contacts = contacts_data
    if search:
        filtered_contacts = [c for c in contacts_data if search.lower() in f"{c['first_name']} {c['last_name']}".lower()]
    if company_id:
        filtered_contacts = [c for c in filtered_contacts if c['company_id'] == company_id]
    
    return {
        "status_code": 200,
        "message": "Contacts fetched successfully",
        "data": {
            "contacts": filtered_contacts,
            "total": len(filtered_contacts),
            "page": page,
            "limit": limit
        }
    }

@app.get("/api/v1/sales/contacts/{contact_id}")
async def get_contact(contact_id: int, user_data: dict = Depends(verify_token)):
    contact = next((c for c in contacts_data if c['id'] == contact_id), None)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return {
        "status_code": 200,
        "message": "Contact fetched successfully",
        "data": contact
    }

@app.post("/api/v1/sales/contacts/")
async def create_contact(contact_data: dict, user_data: dict = Depends(verify_token)):
    new_id = max([c['id'] for c in contacts_data]) + 1 if contacts_data else 1
    new_contact = {
        "id": new_id,
        **contact_data,
        "is_active": True,
        "created_at": "2025-09-02T08:26:02.937087",
        "updated_at": "2025-09-02T08:26:02.937087"
    }
    contacts_data.append(new_contact)
    
    return {
        "status_code": 201,
        "message": "Contact created successfully",
        "data": new_contact
    }

if __name__ == "__main__":
    print("Starting Simple Sales API Server with Authentication...")
    print("Server will be available at: http://localhost:8002")
    print("Test credentials: admin / admin123")
    print("API endpoints:")
    print("  - POST /api/v1/auth/token (login)")
    print("  - GET /api/v1/auth/verify-token/ (verify)")
    print("  - GET /api/v1/sales/companies")
    print("  - GET /api/v1/sales/contacts")
    uvicorn.run(app, host="0.0.0.0", port=8002)