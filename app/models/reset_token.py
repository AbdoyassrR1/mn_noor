#!/usr/bin/python3
from app.app import db, local_timezone
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey


class ResetToken(db.Model):
    __tablename__ = "reset_tokens"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(50), nullable=False, unique=True)
    created_at = Column(DateTime, default=lambda: datetime.now(local_timezone))
    is_used = Column(Boolean, default=False, nullable=False)
    expiry_date = Column(DateTime)

    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)

    def set_expiry_date(self, minutes):
        self.created_at = datetime.now(local_timezone)
        self.expiry_date = self.created_at + timedelta(minutes=minutes)
