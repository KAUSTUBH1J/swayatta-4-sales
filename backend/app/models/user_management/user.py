from sqlalchemy import Column, String, Text, Boolean, DateTime, Enum, ForeignKey, Integer, text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base

class User(Base):
    __tablename__ = 'tbl_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(255))
    username = Column(String(100), unique=True)
    email = Column(String(150), unique=True)
    contact_no = Column(String(15))
    gender = Column(Enum("Male","Female","Other", name="gender_enum"))
    dob = Column(DateTime)
    profile_photo = Column(String(255))

    department_id = Column(Integer, ForeignKey("mst_departments.id"))
    sub_department_id = Column(Integer, ForeignKey("mst_sub_departments.id"))
    designation_id = Column(Integer, ForeignKey("mst_designations.id"))
    is_reporting = Column(Boolean, default=False)
    reporting_to = Column(Integer, ForeignKey("tbl_users.id"), nullable=True)
    region_id = Column(Integer, ForeignKey("mst_regions.id"))
    role_id = Column(Integer, ForeignKey("mst_roles.id"), nullable=True)
    assign_modules = Column(String(100), nullable=True, default=None)
    address = Column(Text)
    business_vertical_id = Column(Integer, ForeignKey("mst_business_verticals.id"))

    password_hash = Column(Text)
    is_password_forgot = Column(Boolean, default=False)
    is_password_changed = Column(Boolean, default=False)
    is_active = Column(Boolean, server_default=text("true"))
    is_deleted = Column(Boolean, server_default=text("false"))

    created_by = Column(Integer, ForeignKey("tbl_users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(Integer, ForeignKey("tbl_users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ---------- Relationships ----------
    department = relationship("Department", lazy="joined", foreign_keys=[department_id])
    sub_department = relationship("SubDepartment", back_populates="users", foreign_keys=[sub_department_id], lazy="joined")
    designation = relationship("Designation", foreign_keys=[designation_id], lazy="joined")
    role = relationship("Role", back_populates="users", foreign_keys=[role_id], lazy="joined")
    region = relationship("Region", lazy="joined", foreign_keys=[region_id])
    business_vertical = relationship("BusinessVertical", lazy="joined", foreign_keys=[business_vertical_id])

    # ---------- Self-referencing ----------
    manager = relationship("User", foreign_keys=[reporting_to], remote_side=[id], lazy="joined")
    created_user = relationship("User", foreign_keys=[created_by], remote_side=[id], lazy="joined", post_update=True)
    updated_user = relationship("User", foreign_keys=[updated_by], remote_side=[id], lazy="joined", post_update=True)
