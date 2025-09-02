from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.core import auth_service as AuthService
from app.schemas.sales import company as CompanySchemas
from app.schemas.sales.DefaultResponse import SalesResponse
from app.utils.responses import Response
from app.services.sales import company_service as CompanyService
from app.core.permissions import check_permission
from app.models.sales.company import Company
from app.schemas.sales.company import CompanyExportOut
from app.utils.export_helper.generic_exporter import export_to_csv

router = APIRouter()

#---------- Helper Function for Consistent Error Handling ----------
def handle_exception(e: Exception, msg: str, code: int = 500):
    return SalesResponse(
        message=f"{msg}: {str(e)}",
        status_code=code,
        data=None
    )

#---------- Create Company ----------
@router.post("/", response_model=SalesResponse, dependencies=[check_permission(2, "/sales/companies", "create")], status_code=status.HTTP_201_CREATED)
def create_company(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    company: CompanySchemas.CompanyCreate,
    db: Session = Depends(get_db)
):
    try:
        login_id = current_user.id
        result = CompanyService.create_company(db, company, login_id)
        return Response(
            message="Company created successfully",
            status_code=status.HTTP_201_CREATED,
            json_data=result
        )
    except Exception as e:
        return handle_exception(e, "Company creation failed", getattr(e, "status_code", 400))

#---------- List Companies ----------
@router.get("/", response_model=SalesResponse, dependencies=[check_permission(2, "/sales/companies", "view")], status_code=status.HTTP_200_OK)
def list_companies(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
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
        return handle_exception(e, "Error fetching companies", getattr(e, "status_code", 500))

#---------- Export Companies ----------
@router.get("/export",
            response_model=CompanySchemas.CompanyExportOut,
            dependencies=[check_permission(2, "/sales/companies", "export")],
            status_code=status.HTTP_200_OK)
def export_companies(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
):
    try:
        companies = db.query(Company).filter(Company.is_deleted == False).all()
        company_list = [CompanyExportOut.from_orm(company) for company in companies]
        return export_to_csv(company_list, CompanyExportOut, filename="companies.csv")
    except Exception as e:
        return handle_exception(e, "Company export failed", getattr(e, "status_code", 500))

#---------- Get Parent Companies for Dropdown ----------
@router.get("/parent-companies", response_model=SalesResponse, dependencies=[check_permission(2, "/sales/companies", "view")], status_code=status.HTTP_200_OK)
def get_parent_companies(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db)
):
    try:
        result = CompanyService.get_parent_companies(db)
        return Response(
            json_data=result,
            message="Parent companies fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error fetching parent companies", getattr(e, "status_code", 500))

#---------- Fetch Single Company by ID ----------
@router.get("/{company_id}", response_model=SalesResponse, dependencies=[check_permission(2, "/sales/companies", "view")], status_code=status.HTTP_200_OK)
def fetch_company(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
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
        return handle_exception(e, "Error fetching company", getattr(e, "status_code", 500))

#---------- Update Company ----------
@router.put("/{company_id}", response_model=CompanySchemas.SalesResponse, dependencies=[check_permission(2, "/sales/companies", "edit")], status_code=status.HTTP_200_OK)
def update_company_details(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    company_id: int,
    company: CompanySchemas.CompanyUpdate,
    db: Session = Depends(get_db)
):
    try:
        login_id = current_user.id
        updated_company = CompanyService.update_company(db, company_id, company, login_id)
        if not updated_company:
            return handle_exception(Exception("Company not found"), "Error updating company", 404)
        return Response(
            json_data=updated_company,
            message="Company updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error updating company", getattr(e, "status_code", 500))

#---------- Delete Company ----------
@router.delete("/{company_id}", response_model=CompanySchemas.SalesResponse, dependencies=[check_permission(2, "/sales/companies", "delete")], status_code=status.HTTP_200_OK)
def delete_company_details(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    company_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = CompanyService.delete_company(db, company_id)
        if not deleted:
            return handle_exception(Exception("Company not found"), "Error deleting company", 404)
        return Response(
            json_data={"id": company_id, "deleted": True},
            message="Company deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error deleting company", getattr(e, "status_code", 500))