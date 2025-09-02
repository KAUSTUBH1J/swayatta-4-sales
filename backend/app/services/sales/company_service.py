from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from app.models.sales.company import Company, CompanyAddress, CompanyTurnover, CompanyProfit, CompanyDocument
from app.schemas.sales.company import (
    CompanyCreate, CompanyUpdate, CompanyResponse, CompanyListResponse,
    CompanyAddressCreate, CompanyTurnoverCreate, CompanyProfitCreate, CompanyDocumentCreate
)
from fastapi import HTTPException, status


def create_company(db: Session, company_data: CompanyCreate, created_by: int) -> CompanyResponse:
    """Create a new company with related data"""
    try:
        # Create main company record
        company = Company(
            gst_no=company_data.gst_no,
            pan_no=company_data.pan_no,
            industry_segment_id=company_data.industry_segment_id,
            company_name=company_data.company_name,
            website=company_data.website,
            is_child=company_data.is_child,
            parent_company_id=company_data.parent_company_id,
            account_type_id=company_data.account_type_id,
            account_sub_type_id=company_data.account_sub_type_id,
            business_type_id=company_data.business_type_id,
            account_region_id=company_data.account_region_id,
            company_profile=company_data.company_profile,
            created_by=created_by
        )
        
        db.add(company)
        db.flush()  # Get the company ID
        
        # Add addresses
        for addr_data in company_data.addresses:
            address = CompanyAddress(
                company_id=company.id,
                address_type_id=addr_data.address_type_id,
                address=addr_data.address,
                country_id=addr_data.country_id,
                state_id=addr_data.state_id,
                city_id=addr_data.city_id,
                zip_code=addr_data.zip_code,
                created_by=created_by
            )
            db.add(address)
        
        # Add turnover records
        for turnover_data in company_data.turnover_records:
            turnover = CompanyTurnover(
                company_id=company.id,
                year=turnover_data.year,
                revenue=turnover_data.revenue,
                currency_id=turnover_data.currency_id,
                created_by=created_by
            )
            db.add(turnover)
        
        # Add profit records
        for profit_data in company_data.profit_records:
            profit = CompanyProfit(
                company_id=company.id,
                year=profit_data.year,
                revenue=profit_data.revenue,
                currency_id=profit_data.currency_id,
                created_by=created_by
            )
            db.add(profit)
        
        # Add documents
        for doc_data in company_data.documents:
            document = CompanyDocument(
                company_id=company.id,
                document_type_id=doc_data.document_type_id,
                file_name=doc_data.file_name,
                file_path=doc_data.file_path,
                file_size=doc_data.file_size,
                description=doc_data.description,
                created_by=created_by
            )
            db.add(document)
        
        db.commit()
        db.refresh(company)
        
        return CompanyResponse.from_orm(company)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating company: {str(e)}"
        )


def get_companies(
    db: Session, 
    skip: int = 0, 
    limit: int = 10, 
    search: Optional[str] = None
) -> CompanyListResponse:
    """Get list of companies with pagination and search"""
    query = db.query(Company).filter(Company.is_deleted == False)
    
    if search:
        query = query.filter(
            or_(
                Company.company_name.ilike(f"%{search}%"),
                Company.gst_no.ilike(f"%{search}%"),
                Company.pan_no.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    companies = query.offset(skip).limit(limit).all()
    
    return CompanyListResponse(
        companies=[CompanyResponse.from_orm(company) for company in companies],
        total=total,
        page=(skip // limit) + 1,
        limit=limit
    )


def get_company_by_id(db: Session, company_id: int) -> Optional[CompanyResponse]:
    """Get company by ID"""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.is_deleted == False
    ).first()
    
    if company:
        return CompanyResponse.from_orm(company)
    return None


def update_company(
    db: Session, 
    company_id: int, 
    company_data: CompanyUpdate, 
    updated_by: int
) -> Optional[CompanyResponse]:
    """Update company and related data"""
    try:
        company = db.query(Company).filter(
            Company.id == company_id,
            Company.is_deleted == False
        ).first()
        
        if not company:
            return None
        
        # Update main company fields
        for field, value in company_data.dict(exclude_unset=True, exclude={'addresses', 'turnover_records', 'profit_records', 'documents'}).items():
            setattr(company, field, value)
        company.updated_by = updated_by
        
        # Update addresses (simple approach: delete and recreate)
        if company_data.addresses is not None:
            # Delete existing addresses
            db.query(CompanyAddress).filter(CompanyAddress.company_id == company_id).delete()
            
            # Add new addresses
            for addr_data in company_data.addresses:
                address = CompanyAddress(
                    company_id=company.id,
                    address_type_id=addr_data.address_type_id,
                    address=addr_data.address,
                    country_id=addr_data.country_id,
                    state_id=addr_data.state_id,
                    city_id=addr_data.city_id,
                    zip_code=addr_data.zip_code,
                    created_by=updated_by
                )
                db.add(address)
        
        # Similar updates for turnover, profit, and documents
        if company_data.turnover_records is not None:
            db.query(CompanyTurnover).filter(CompanyTurnover.company_id == company_id).delete()
            for turnover_data in company_data.turnover_records:
                turnover = CompanyTurnover(
                    company_id=company.id,
                    year=turnover_data.year,
                    revenue=turnover_data.revenue,
                    currency_id=turnover_data.currency_id,
                    created_by=updated_by
                )
                db.add(turnover)
        
        if company_data.profit_records is not None:
            db.query(CompanyProfit).filter(CompanyProfit.company_id == company_id).delete()
            for profit_data in company_data.profit_records:
                profit = CompanyProfit(
                    company_id=company.id,
                    year=profit_data.year,
                    revenue=profit_data.revenue,
                    currency_id=profit_data.currency_id,
                    created_by=updated_by
                )
                db.add(profit)
        
        if company_data.documents is not None:
            db.query(CompanyDocument).filter(CompanyDocument.company_id == company_id).delete()
            for doc_data in company_data.documents:
                document = CompanyDocument(
                    company_id=company.id,
                    document_type_id=doc_data.document_type_id,
                    file_name=doc_data.file_name,
                    file_path=doc_data.file_path,
                    file_size=doc_data.file_size,
                    description=doc_data.description,
                    created_by=updated_by
                )
                db.add(document)
        
        db.commit()
        db.refresh(company)
        
        return CompanyResponse.from_orm(company)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating company: {str(e)}"
        )


def delete_company(db: Session, company_id: int) -> bool:
    """Soft delete company"""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.is_deleted == False
    ).first()
    
    if not company:
        return False
    
    company.is_deleted = True
    db.commit()
    return True


def get_parent_companies(db: Session) -> List[dict]:
    """Get list of companies that can be parent companies"""
    companies = db.query(Company).filter(
        Company.is_deleted == False,
        Company.is_active == True
    ).all()
    
    return [{"id": company.id, "name": company.company_name} for company in companies]