from sqlalchemy import Column, Boolean, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base

class UserPermission(Base):
    __tablename__ = 'tbl_user_permissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('tbl_users.id'))
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
    user = relationship("User", lazy="joined", foreign_keys=[user_id])
    module = relationship("Module", lazy="joined", foreign_keys=[module_id])
    menu = relationship("Menu", lazy="joined", foreign_keys=[menu_id])
    created_user = relationship("User", foreign_keys=[created_by], lazy="joined", post_update=True)
    updated_user = relationship("User", foreign_keys=[updated_by], lazy="joined", post_update=True)
