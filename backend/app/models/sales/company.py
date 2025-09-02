from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base

class Company(Base):
    __tablename__ = 'tbl_companies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # General Info
    gst_no = Column(String(15))
    pan_no = Column(String(10))
    industry_segment_id = Column(Integer)  # Remove FK for now
    company_name = Column(String(255), nullable=False)
    website = Column(String(255))
    is_child = Column(Boolean, default=False)
    parent_company_id = Column(Integer, ForeignKey("tbl_companies.id"), nullable=True)
    
    # Account Details
    account_type_id = Column(Integer)  # Remove FK for now
    account_sub_type_id = Column(Integer)  # Remove FK for now
    business_type_id = Column(Integer)  # Remove FK for now
    account_region_id = Column(Integer)  # Remove FK for now
    
    # Company Profile
    company_profile = Column(Text)
    
    # Standard fields
    is_active = Column(Boolean, server_default=text("true"))
    is_deleted = Column(Boolean, server_default=text("false"))
    created_by = Column(Integer, nullable=True)  # Remove FK for now
    updated_by = Column(Integer, nullable=True)  # Remove FK for now
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Self-referencing relationship for parent-child companies
    parent_company = relationship("Company", remote_side=[id], back_populates="child_companies")
    child_companies = relationship("Company", back_populates="parent_company", cascade="all, delete-orphan")
    
    # One-to-many relationships
    addresses = relationship("CompanyAddress", back_populates="company", cascade="all, delete-orphan")
    turnover_records = relationship("CompanyTurnover", back_populates="company", cascade="all, delete-orphan")
    profit_records = relationship("CompanyProfit", back_populates="company", cascade="all, delete-orphan")
    documents = relationship("CompanyDocument", back_populates="company", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")


class CompanyAddress(Base):
    __tablename__ = 'tbl_company_addresses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("tbl_companies.id"), nullable=False)
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
    company = relationship("Company", back_populates="addresses")


class CompanyTurnover(Base):
    __tablename__ = 'tbl_company_turnover'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("tbl_companies.id"), nullable=False)
    year = Column(Integer, nullable=False)
    revenue = Column(Numeric(15, 2))
    currency_id = Column(Integer)  # Remove FK for now
    
    # Standard fields
    is_active = Column(Boolean, server_default=text("true"))
    is_deleted = Column(Boolean, server_default=text("false"))
    created_by = Column(Integer, nullable=True)  # Remove FK for now
    updated_by = Column(Integer, nullable=True)  # Remove FK for now
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="turnover_records")


class CompanyProfit(Base):
    __tablename__ = 'tbl_company_profit'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("tbl_companies.id"), nullable=False)
    year = Column(Integer, nullable=False)
    revenue = Column(Numeric(15, 2))
    currency_id = Column(Integer)  # Remove FK for now
    
    # Standard fields
    is_active = Column(Boolean, server_default=text("true"))
    is_deleted = Column(Boolean, server_default=text("false"))
    created_by = Column(Integer, nullable=True)  # Remove FK for now
    updated_by = Column(Integer, nullable=True)  # Remove FK for now
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="profit_records")


class CompanyDocument(Base):
    __tablename__ = 'tbl_company_documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("tbl_companies.id"), nullable=False)
    document_type_id = Column(Integer)  # Remove FK for now
    file_name = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)
    description = Column(Text)
    
    # Standard fields
    is_active = Column(Boolean, server_default=text("true"))
    is_deleted = Column(Boolean, server_default=text("false"))
    created_by = Column(Integer, nullable=True)  # Remove FK for now
    updated_by = Column(Integer, nullable=True)  # Remove FK for now
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="documents")