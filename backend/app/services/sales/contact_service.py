from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from app.models.sales.contact import Contact, ContactAddress
from app.schemas.sales.contact import (
    ContactCreate, ContactUpdate, ContactResponse, ContactListResponse
)
from fastapi import HTTPException, status


def create_contact(db: Session, contact_data: ContactCreate, created_by: int) -> ContactResponse:
    """Create a new contact with related data"""
    try:
        # Create main contact record
        contact = Contact(
            title_id=contact_data.title_id,
            first_name=contact_data.first_name,
            middle_name=contact_data.middle_name,
            last_name=contact_data.last_name,
            dob=contact_data.dob,
            company_id=contact_data.company_id,
            designation_id=contact_data.designation_id,
            email=contact_data.email,
            fax=contact_data.fax,
            primary_no=contact_data.primary_no,
            secondary_no=contact_data.secondary_no,
            alternate_no=contact_data.alternate_no,
            dont_solicit=contact_data.dont_solicit,
            dont_mail=contact_data.dont_mail,
            dont_fax=contact_data.dont_fax,
            dont_email=contact_data.dont_email,
            dont_call=contact_data.dont_call,
            created_by=created_by
        )
        
        db.add(contact)
        db.flush()  # Get the contact ID
        
        # Add addresses
        for addr_data in contact_data.addresses:
            address = ContactAddress(
                contact_id=contact.id,
                address_type_id=addr_data.address_type_id,
                address=addr_data.address,
                country_id=addr_data.country_id,
                state_id=addr_data.state_id,
                city_id=addr_data.city_id,
                zip_code=addr_data.zip_code,
                created_by=created_by
            )
            db.add(address)
        
        db.commit()
        db.refresh(contact)
        
        return ContactResponse.from_orm(contact)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating contact: {str(e)}"
        )


def get_contacts(
    db: Session, 
    skip: int = 0, 
    limit: int = 10, 
    search: Optional[str] = None,
    company_id: Optional[int] = None
) -> ContactListResponse:
    """Get list of contacts with pagination and search"""
    query = db.query(Contact).filter(Contact.is_deleted == False)
    
    if company_id:
        query = query.filter(Contact.company_id == company_id)
    
    if search:
        query = query.filter(
            or_(
                Contact.first_name.ilike(f"%{search}%"),
                Contact.last_name.ilike(f"%{search}%"),
                Contact.email.ilike(f"%{search}%"),
                Contact.primary_no.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    contacts = query.offset(skip).limit(limit).all()
    
    return ContactListResponse(
        contacts=[ContactResponse.from_orm(contact) for contact in contacts],
        total=total,
        page=(skip // limit) + 1,
        limit=limit
    )


def get_contact_by_id(db: Session, contact_id: int) -> Optional[ContactResponse]:
    """Get contact by ID"""
    contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.is_deleted == False
    ).first()
    
    if contact:
        return ContactResponse.from_orm(contact)
    return None


def update_contact(
    db: Session, 
    contact_id: int, 
    contact_data: ContactUpdate, 
    updated_by: int
) -> Optional[ContactResponse]:
    """Update contact and related data"""
    try:
        contact = db.query(Contact).filter(
            Contact.id == contact_id,
            Contact.is_deleted == False
        ).first()
        
        if not contact:
            return None
        
        # Update main contact fields
        for field, value in contact_data.dict(exclude_unset=True, exclude={'addresses'}).items():
            setattr(contact, field, value)
        contact.updated_by = updated_by
        
        # Update addresses (simple approach: delete and recreate)
        if contact_data.addresses is not None:
            # Delete existing addresses
            db.query(ContactAddress).filter(ContactAddress.contact_id == contact_id).delete()
            
            # Add new addresses
            for addr_data in contact_data.addresses:
                address = ContactAddress(
                    contact_id=contact.id,
                    address_type_id=addr_data.address_type_id,
                    address=addr_data.address,
                    country_id=addr_data.country_id,
                    state_id=addr_data.state_id,
                    city_id=addr_data.city_id,
                    zip_code=addr_data.zip_code,
                    created_by=updated_by
                )
                db.add(address)
        
        db.commit()
        db.refresh(contact)
        
        return ContactResponse.from_orm(contact)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating contact: {str(e)}"
        )


def delete_contact(db: Session, contact_id: int) -> bool:
    """Soft delete contact"""
    contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.is_deleted == False
    ).first()
    
    if not contact:
        return False
    
    contact.is_deleted = True
    db.commit()
    return True


def get_contacts_by_company(db: Session, company_id: int) -> List[ContactResponse]:
    """Get all contacts for a specific company"""
    contacts = db.query(Contact).filter(
        Contact.company_id == company_id,
        Contact.is_deleted == False
    ).all()
    
    return [ContactResponse.from_orm(contact) for contact in contacts]