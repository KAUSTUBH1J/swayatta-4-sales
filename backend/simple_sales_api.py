#!/usr/bin/env python3
"""
Simple Sales API Server for Testing
Uses in-memory data to simulate the Sales API endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="Simple Sales API for Testing")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory data
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

# Root endpoints
@app.get("/")
async def root():
    return {"message": "Simple Sales API Test Server", "status": "running"}

@app.get("/api/v1/")
async def api_root():
    return {"message": "Sales API v1", "endpoints": ["/sales/companies", "/sales/contacts"]}

# Companies endpoints
@app.get("/api/v1/sales/companies/")
async def list_companies(page: int = 1, limit: int = 10, search: str = None):
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
async def get_company(company_id: int):
    company = next((c for c in companies_data if c['id'] == company_id), None)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return {
        "status_code": 200,
        "message": "Company fetched successfully",
        "data": company
    }

@app.post("/api/v1/sales/companies/")
async def create_company(company_data: dict):
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
async def get_parent_companies():
    parent_companies = [{"id": c['id'], "name": c['company_name']} for c in companies_data]
    return {
        "status_code": 200,
        "message": "Parent companies fetched successfully",
        "data": parent_companies
    }

# Contacts endpoints
@app.get("/api/v1/sales/contacts/")
async def list_contacts(page: int = 1, limit: int = 10, search: str = None, company_id: int = None):
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
async def get_contact(contact_id: int):
    contact = next((c for c in contacts_data if c['id'] == contact_id), None)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return {
        "status_code": 200,
        "message": "Contact fetched successfully",
        "data": contact
    }

@app.post("/api/v1/sales/contacts/")
async def create_contact(contact_data: dict):
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
    print("Starting Simple Sales API Server...")
    print("Server will be available at: http://localhost:8002")
    print("API endpoints:")
    print("  - GET /api/v1/sales/companies")
    print("  - GET /api/v1/sales/contacts")
    uvicorn.run(app, host="0.0.0.0", port=8002)