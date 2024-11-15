#!/usr/bin/python3
from app.app import db, local_timezone
from app.models.base import BaseModel
from app.models.user import User
from datetime import datetime
from sqlalchemy import Column, Integer, Enum, Float, String, Text


class Package(BaseModel):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    package = Column(String(50), nullable=False, unique=True)
    session_type = Column(Enum("private", "group"), nullable=False)
    price = Column(Float, nullable=False)
    duration = Column(Integer, nullable=False)
    max_sessions = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
