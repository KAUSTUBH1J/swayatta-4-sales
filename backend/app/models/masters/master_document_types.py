from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


class DocumentType(Base):
    __tablename__ = "document_types"

    document_type_id = Column(BigInteger, primary_key=True, autoincrement=True)
    document_type_name = Column(String(100), unique=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by = Column(BigInteger, ForeignKey("tbl_users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(BigInteger, ForeignKey("tbl_users.id", ondelete="SET NULL"), nullable=True)

    is_active = Column(Boolean, server_default=text("true"))
    is_deleted = Column(Boolean, server_default=text("false"))

    # relationships with User (if needed)
    created_user = relationship("User", foreign_keys=[created_by], lazy="joined", post_update=True)
    updated_user = relationship("User", foreign_keys=[updated_by], lazy="joined", post_update=True)
