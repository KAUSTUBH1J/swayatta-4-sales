from sqlalchemy import Column, Boolean, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base

class RolePermission(Base):
    __tablename__ = 'tbl_role_permissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('mst_roles.id'))
    module_id = Column(Integer, ForeignKey('mst_modules.id'))
    menu_id = Column(Integer, ForeignKey('mst_menus.id'))
    permission_ids = Column(String(255))
    is_active = Column(Boolean, server_default=text("true"))
    is_deleted = Column(Boolean, server_default=text("false"))

    created_by = Column(Integer, ForeignKey('tbl_users.id', ondelete="SET NULL"), nullable=True)
    updated_by = Column(Integer, ForeignKey('tbl_users.id', ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    role = relationship("Role", lazy="joined")
    module = relationship("Module", lazy="joined")
    menu = relationship("Menu", lazy="joined")
    created_user = relationship("User", foreign_keys=[created_by], lazy="joined", post_update=True)
    updated_user = relationship("User", foreign_keys=[updated_by], lazy="joined", post_update=True)
