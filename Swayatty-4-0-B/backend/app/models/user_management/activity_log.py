from sqlalchemy import (Column, Integer, String, Text, DateTime, ForeignKey)
from datetime import datetime
from app.database.db import Base

class ActivityLog(Base):
    __tablename__ = 'activity_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action_type = Column(String(50), nullable=False)
    description = Column(Text)
    menu_name = Column(String(100))
    record_id = Column(Integer)
    remarks = Column(Text)
    ip_address = Column(String(45))
    device_info = Column(Text)
    logged_at = Column(DateTime, default=datetime.utcnow)
