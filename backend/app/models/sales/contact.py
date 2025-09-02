from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base

class Contact(Base):
    __tablename__ = 'tbl_contacts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # General Info
    title_id = Column(Integer)  # Remove FK for now
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    last_name = Column(String(100))
    dob = Column(Date)
    company_id = Column(Integer, ForeignKey("tbl_companies.id"), nullable=False)
    designation_id = Column(Integer)  # Remove FK for now
    email = Column(String(150))
    fax = Column(String(20))
    primary_no = Column(String(15))
    secondary_no = Column(String(15))
    alternate_no = Column(String(15))
    
    # Communication Preferences
    dont_solicit = Column(Boolean, default=False)
    dont_mail = Column(Boolean, default=False)
    dont_fax = Column(Boolean, default=False)
    dont_email = Column(Boolean, default=False)
    dont_call = Column(Boolean, default=False)
    
    # Standard fields
    is_active = Column(Boolean, server_default=text("true"))
    is_deleted = Column(Boolean, server_default=text("false"))
    created_by = Column(Integer, nullable=True)  # Remove FK for now
    updated_by = Column(Integer, nullable=True)  # Remove FK for now
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="contacts")
    
    # One-to-many relationships
    addresses = relationship("ContactAddress", back_populates="contact", cascade="all, delete-orphan")


class ContactAddress(Base):
    __tablename__ = 'tbl_contact_addresses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contact_id = Column(Integer, ForeignKey("tbl_contacts.id"), nullable=False)
    address_type_id = Column(Integer)  # Remove FK for now
    address = Column(Text)
    country_id = Column(Integer)  # Remove FK for now
    state_id = Column(Integer)  # Remove FK for now
    city_id = Column(Integer)  # Remove FK for now
    zip_code = Column(String(10))
    
    # Standard fields
    is_active = Column(Boolean, server_default=text("true"))
    is_deleted = Column(Boolean, server_default=text("false"))
    created_by = Column(Integer, nullable=True)  # Remove FK for now
    updated_by = Column(Integer, nullable=True)  # Remove FK for now
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contact = relationship("Contact", back_populates="addresses")