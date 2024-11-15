#!/usr/bin/python3
from app.app import db, local_timezone
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime


class UserSession(db.Model):
    __tablename__ = "user_sessions"

    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, primary_key=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(local_timezone))
