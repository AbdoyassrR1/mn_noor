#!/usr/bin/python3
from app.app import db, local_timezone
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship


class Language(db.Model):
    __tablename__ = 'languages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    language = Column(String(10), nullable=False, unique=True)
    created_at = Column(DateTime, default=lambda: datetime.now(local_timezone))

    users = relationship("User", backref="language")
