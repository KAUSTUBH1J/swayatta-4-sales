from fastapi import FastAPI
from app.routers.api import api_router
from app.database.db import Base, engine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FastAPI User Auth CRUD")

# Create tables on startup
Base.metadata.create_all(bind=engine)

app.include_router(api_router)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         
    allow_credentials=True,
    allow_methods=["*"],        
    allow_headers=["*"],          
)
