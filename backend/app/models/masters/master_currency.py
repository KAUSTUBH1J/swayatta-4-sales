from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


class MasterCurrency(Base):
    __tablename__ = "master_currencies"

    currency_id = Column(Integer, primary_key=True, autoincrement=True)
    currency_code = Column(String(10), unique=True, nullable=False)
    currency_name = Column(String(50), nullable=False)
    symbol = Column(String(10), nullable=True)

    is_active = Column(Boolean, server_default=text("true"))
    is_deleted = Column(Boolean, server_default=text("false"))

    created_by = Column(Integer, ForeignKey('tbl_users.id', ondelete="SET NULL"), nullable=True)
    updated_by = Column(Integer, ForeignKey('tbl_users.id', ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_user = relationship("User", foreign_keys=[created_by], lazy="joined", post_update=True)
    updated_user = relationship("User", foreign_keys=[updated_by], lazy="joined", post_update=True)
