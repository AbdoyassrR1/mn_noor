#!/usr/bin/python3
from app.app import db, local_timezone
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean


class UserPackage(db.Model):
    __tablename__ = "user_packages"

    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, primary_key=True)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False, primary_key=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(local_timezone))
    expiry_date = Column(DateTime)
    is_active = Column(Boolean, default=False, nullable=False)

    def set_expiry_date(self, days):
        self.timestamp = datetime.now(local_timezone)
        if days == 0:
            self.expiry_date = self.timestamp
        else:
            self.expiry_date = self.timestamp + timedelta(days=days)
