#!/usr/bin/python3
from app.models.base import BaseModel
from datetime import datetime
from sqlalchemy import Column, String, Integer, Date, Enum


class Group(BaseModel):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group = Column(String(50), nullable=False, unique=True)
    size = Column(Integer, nullable=False)
    days = Column(String(30), nullable=False)
    status = Column(Enum("coming", "running", "finished"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
