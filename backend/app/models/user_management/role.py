from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Integer, text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base

class Role(Base):
    __tablename__ = 'mst_roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, server_default=text("true"))
    is_deleted = Column(Boolean, server_default=text("false"))

    created_by = Column(Integer, ForeignKey('tbl_users.id', ondelete="SET NULL"), nullable=True)
    updated_by = Column(Integer, ForeignKey('tbl_users.id', ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_user = relationship("User", foreign_keys=[created_by], lazy="joined", post_update=True)
    updated_user = relationship("User", foreign_keys=[updated_by], lazy="joined", post_update=True)
    users = relationship("User", back_populates="role", foreign_keys="User.role_id")
