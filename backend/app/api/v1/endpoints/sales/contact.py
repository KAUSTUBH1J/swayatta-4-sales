from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.core import auth_service as AuthService
from app.schemas.sales import contact as ContactSchemas
from app.schemas.sales.DefaultResponse import SalesResponse
from app.utils.responses import Response
from app.services.sales import contact_service as ContactService
from app.core.permissions import check_permission
from app.models.sales.contact import Contact
from app.schemas.sales.contact import ContactExportOut
from app.utils.export_helper.generic_exporter import export_to_csv

router = APIRouter()

#---------- Helper Function for Consistent Error Handling ----------
def handle_exception(e: Exception, msg: str, code: int = 500):
    return SalesResponse(
        message=f"{msg}: {str(e)}",
        status_code=code,
        data=None
    )

#---------- Create Contact ----------
@router.post("/", response_model=ContactSchemas.SalesResponse, dependencies=[check_permission(2, "/sales/contacts", "create")], status_code=status.HTTP_201_CREATED)
def create_contact(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    contact: ContactSchemas.ContactCreate,
    db: Session = Depends(get_db)
):
    try:
        login_id = current_user.id
        result = ContactService.create_contact(db, contact, login_id)
        return Response(
            message="Contact created successfully",
            status_code=status.HTTP_201_CREATED,
            json_data=result
        )
    except Exception as e:
        return handle_exception(e, "Contact creation failed", getattr(e, "status_code", 400))

#---------- List Contacts ----------
@router.get("/", response_model=ContactSchemas.SalesResponse, dependencies=[check_permission(2, "/sales/contacts", "view")], status_code=status.HTTP_200_OK)
def list_contacts(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None),
    company_id: Optional[int] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = ContactService.get_contacts(db, skip=offset, limit=limit, search=search, company_id=company_id)
        return Response(
            json_data=result, 
            message="Contacts fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error fetching contacts", getattr(e, "status_code", 500))

#---------- Export Contacts ----------
@router.get("/export",
            response_model=ContactSchemas.ContactExportOut,
            dependencies=[check_permission(2, "/sales/contacts", "export")],
            status_code=status.HTTP_200_OK)
def export_contacts(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
):
    try:
        contacts = db.query(Contact).filter(Contact.is_deleted == False).all()
        contact_list = [ContactExportOut.from_orm(contact) for contact in contacts]
        return export_to_csv(contact_list, ContactExportOut, filename="contacts.csv")
    except Exception as e:
        return handle_exception(e, "Contact export failed", getattr(e, "status_code", 500))

#---------- Get Contacts by Company ----------
@router.get("/by-company/{company_id}", response_model=ContactSchemas.SalesResponse, dependencies=[check_permission(2, "/sales/contacts", "view")], status_code=status.HTTP_200_OK)
def get_contacts_by_company(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    company_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = ContactService.get_contacts_by_company(db, company_id)
        return Response(
            json_data=result,
            message="Contacts fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error fetching contacts", getattr(e, "status_code", 500))

#---------- Fetch Single Contact by ID ----------
@router.get("/{contact_id}", response_model=ContactSchemas.SalesResponse, dependencies=[check_permission(2, "/sales/contacts", "view")], status_code=status.HTTP_200_OK)
def fetch_contact(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    contact_id: int,
    db: Session = Depends(get_db)
):
    try:
        contact = ContactService.get_contact_by_id(db, contact_id)
        if not contact:
            return handle_exception(Exception("Contact not found"), "Error fetching contact", 404)
        return Response(
            json_data=contact,
            message="Contact fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error fetching contact", getattr(e, "status_code", 500))

#---------- Update Contact ----------
@router.put("/{contact_id}", response_model=ContactSchemas.SalesResponse, dependencies=[check_permission(2, "/sales/contacts", "edit")], status_code=status.HTTP_200_OK)
def update_contact_details(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    contact_id: int,
    contact: ContactSchemas.ContactUpdate,
    db: Session = Depends(get_db)
):
    try:
        login_id = current_user.id
        updated_contact = ContactService.update_contact(db, contact_id, contact, login_id)
        if not updated_contact:
            return handle_exception(Exception("Contact not found"), "Error updating contact", 404)
        return Response(
            json_data=updated_contact,
            message="Contact updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error updating contact", getattr(e, "status_code", 500))

#---------- Delete Contact ----------
@router.delete("/{contact_id}", response_model=ContactSchemas.SalesResponse, dependencies=[check_permission(2, "/sales/contacts", "delete")], status_code=status.HTTP_200_OK)
def delete_contact_details(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    contact_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = ContactService.delete_contact(db, contact_id)
        if not deleted:
            return handle_exception(Exception("Contact not found"), "Error deleting contact", 404)
        return Response(
            json_data={"id": contact_id, "deleted": True},
            message="Contact deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error deleting contact", getattr(e, "status_code", 500))