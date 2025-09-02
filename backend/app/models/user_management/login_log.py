from sqlalchemy import (
    Column, Integer, String, Text, Enum, Boolean, DateTime, ForeignKey
)
from datetime import datetime
from app.database.db import Base

class LoginLog(Base):
    __tablename__ = 'login_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    login_id = Column(String(100), nullable=False)
    ip_address = Column(String(45))
    device_info = Column(Text)
    location = Column(String(255))
    login_status = Column(Enum('Success', 'Failed', name='login_status_enum'), nullable=False)
    reason = Column(Text)
    logged_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
