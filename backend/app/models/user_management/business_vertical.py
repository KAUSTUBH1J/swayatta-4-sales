from sqlalchemy import Column, Integer, String, Boolean, text
from app.database.db import Base 

class BusinessVertical(Base):
    __tablename__ = "business_verticals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_vertical_name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, server_default=text("true"))
    is_deleted = Column(Boolean, server_default=text("false"))