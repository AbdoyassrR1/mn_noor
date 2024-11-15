#!/usr/bin/python3
from uuid import uuid4
from app.app import db, local_timezone
from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, String,  DateTime


class BaseModel(db.Model):
    __abstract__ = True  # This makes the class abstract and not directly mapped to a table

    id = Column(String(50), primary_key=True, default=lambda: str(uuid4()))
    created_at = Column(DateTime, default=lambda: datetime.now(local_timezone))
    updated_at = Column(DateTime, default=lambda: datetime.now(local_timezone), onupdate=lambda: datetime.now(local_timezone))
