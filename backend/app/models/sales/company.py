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
    industry_segment_id = Column(Integer, ForeignKey("mst_industry_segments.id"))
    company_name = Column(String(255), nullable=False)
    website = Column(String(255))
    is_child = Column(Boolean, default=False)
    parent_company_id = Column(Integer, ForeignKey("tbl_companies.id"), nullable=True)
    
    # Account Details
    account_type_id = Column(Integer, ForeignKey("mst_account_types.id"))
    account_sub_type_id = Column(Integer, ForeignKey("mst_account_sub_types.id"))
    business_type_id = Column(Integer, ForeignKey("mst_business_types.id"))
    account_region_id = Column(Integer, ForeignKey("mst_regions.id"))
    
    # Company Profile
    company_profile = Column(Text)
    
    # Standard fields
    is_active = Column(Boolean, server_default=text("true"))
    is_deleted = Column(Boolean, server_default=text("false"))
    created_by = Column(Integer, ForeignKey("tbl_users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(Integer, ForeignKey("tbl_users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    industry_segment = relationship("IndustrySegment", lazy="joined", foreign_keys=[industry_segment_id])
    parent_company = relationship("Company", remote_side=[id], back_populates="child_companies", lazy="joined")
    child_companies = relationship("Company", back_populates="parent_company", cascade="all, delete-orphan", lazy="select")
    account_type = relationship("AccountType", lazy="joined", foreign_keys=[account_type_id])
    account_sub_type = relationship("AccountSubType", lazy="joined", foreign_keys=[account_sub_type_id])
    business_type = relationship("BusinessType", lazy="joined", foreign_keys=[business_type_id])
    account_region = relationship("Region", lazy="joined", foreign_keys=[account_region_id])
    created_user = relationship("User", foreign_keys=[created_by], lazy="joined", post_update=True)
    updated_user = relationship("User", foreign_keys=[updated_by], lazy="joined", post_update=True)
    
    # One-to-many relationships
    addresses = relationship("CompanyAddress", back_populates="company", cascade="all, delete-orphan", lazy="select")
    turnover_records = relationship("CompanyTurnover", back_populates="company", cascade="all, delete-orphan", lazy="select")
    profit_records = relationship("CompanyProfit", back_populates="company", cascade="all, delete-orphan", lazy="select")
    documents = relationship("CompanyDocument", back_populates="company", cascade="all, delete-orphan", lazy="select")
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan", lazy="select")


class CompanyAddress(Base):
    __tablename__ = 'tbl_company_addresses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("tbl_companies.id"), nullable=False)
    address_type_id = Column(Integer, ForeignKey("mst_address_types.id"))
    address = Column(Text)
    country_id = Column(Integer, ForeignKey("mst_countries.id"))
    state_id = Column(Integer, ForeignKey("mst_states.id"))
    city_id = Column(Integer, ForeignKey("mst_cities.id"))
    zip_code = Column(String(10))
    
    # Standard fields
    is_active = Column(Boolean, server_default=text("true"))
    is_deleted = Column(Boolean, server_default=text("false"))
    created_by = Column(Integer, ForeignKey("tbl_users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(Integer, ForeignKey("tbl_users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="addresses")
    address_type = relationship("AddressType", lazy="joined", foreign_keys=[address_type_id])
    country = relationship("Country", lazy="joined", foreign_keys=[country_id])
    state = relationship("State", lazy="joined", foreign_keys=[state_id])
    city = relationship("City", lazy="joined", foreign_keys=[city_id])
    created_user = relationship("User", foreign_keys=[created_by], lazy="joined", post_update=True)
    updated_user = relationship("User", foreign_keys=[updated_by], lazy="joined", post_update=True)


class CompanyTurnover(Base):
    __tablename__ = 'tbl_company_turnover'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("tbl_companies.id"), nullable=False)
    year = Column(Integer, nullable=False)
    revenue = Column(Numeric(15, 2))
    currency_id = Column(Integer, ForeignKey("mst_currencies.id"))
    
    # Standard fields
    is_active = Column(Boolean, server_default=text("true"))
    is_deleted = Column(Boolean, server_default=text("false"))
    created_by = Column(Integer, ForeignKey("tbl_users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(Integer, ForeignKey("tbl_users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="turnover_records")
    currency = relationship("Currency", lazy="joined", foreign_keys=[currency_id])
    created_user = relationship("User", foreign_keys=[created_by], lazy="joined", post_update=True)
    updated_user = relationship("User", foreign_keys=[updated_by], lazy="joined", post_update=True)


class CompanyProfit(Base):
    __tablename__ = 'tbl_company_profit'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("tbl_companies.id"), nullable=False)
    year = Column(Integer, nullable=False)
    revenue = Column(Numeric(15, 2))
    currency_id = Column(Integer, ForeignKey("mst_currencies.id"))
    
    # Standard fields
    is_active = Column(Boolean, server_default=text("true"))
    is_deleted = Column(Boolean, server_default=text("false"))
    created_by = Column(Integer, ForeignKey("tbl_users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(Integer, ForeignKey("tbl_users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="profit_records")
    currency = relationship("Currency", lazy="joined", foreign_keys=[currency_id])
    created_user = relationship("User", foreign_keys=[created_by], lazy="joined", post_update=True)
    updated_user = relationship("User", foreign_keys=[updated_by], lazy="joined", post_update=True)


class CompanyDocument(Base):
    __tablename__ = 'tbl_company_documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("tbl_companies.id"), nullable=False)
    document_type_id = Column(Integer, ForeignKey("mst_document_types.id"))
    file_name = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)
    description = Column(Text)
    
    # Standard fields
    is_active = Column(Boolean, server_default=text("true"))
    is_deleted = Column(Boolean, server_default=text("false"))
    created_by = Column(Integer, ForeignKey("tbl_users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(Integer, ForeignKey("tbl_users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="documents")
    document_type = relationship("DocumentType", lazy="joined", foreign_keys=[document_type_id])
    created_user = relationship("User", foreign_keys=[created_by], lazy="joined", post_update=True)
    updated_user = relationship("User", foreign_keys=[updated_by], lazy="joined", post_update=True)