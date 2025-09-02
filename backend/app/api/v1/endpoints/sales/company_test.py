from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.sales import company as CompanySchemas
from app.utils.responses import Response
from app.services.sales import company_service as CompanyService

router = APIRouter()

#---------- Helper Function for Consistent Error Handling ----------
def handle_exception(e: Exception, msg: str, code: int = 500):
    return {
        "message": f"{msg}: {str(e)}",
        "status_code": code,
        "data": None
    }

#---------- List Companies (No Auth for Testing) ----------
@router.get("/", status_code=status.HTTP_200_OK)
def list_companies_test(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = CompanyService.get_companies(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result, 
            message="Companies fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error fetching companies", 500)

#---------- Create Company (No Auth for Testing) ----------
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_company_test(
    company: CompanySchemas.CompanyCreate,
    db: Session = Depends(get_db)
):
    try:
        result = CompanyService.create_company(db, company, created_by=1)  # Use dummy user ID
        return Response(
            message="Company created successfully",
            status_code=status.HTTP_201_CREATED,
            json_data=result
        )
    except Exception as e:
        return handle_exception(e, "Company creation failed", 400)

#---------- Get Single Company (No Auth for Testing) ----------
@router.get("/{company_id}", status_code=status.HTTP_200_OK)
def fetch_company_test(
    company_id: int,
    db: Session = Depends(get_db)
):
    try:
        company = CompanyService.get_company_by_id(db, company_id)
        if not company:
            return handle_exception(Exception("Company not found"), "Error fetching company", 404)
        return Response(
            json_data=company,
            message="Company fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error fetching company", 500)