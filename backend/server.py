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

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

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
