from fastapi import FastAPI
from app.database.db import Base, engine
from app.api.v1.endpoints.sales import company_test
from fastapi.middleware.cors import CORSMiddleware

# Create the test app
app = FastAPI(title="Sales API Test")

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include test routes
app.include_router(company_test.router, prefix="/api/v1/sales/companies", tags=["Companies Test"])

@app.get("/api/v1/")
async def root():
    return {"message": "Sales API Test Server Running", "status": "ok"}

@app.get("/")
async def health():
    return {"message": "Sales API Test Server", "endpoints": ["/api/v1/sales/companies"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)