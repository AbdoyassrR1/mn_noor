#!/usr/bin/python3
from app.app import db
from sqlalchemy import Column, Integer, Enum


class Day(db.Model):
    __tablename__ = "days"

    id = Column(Integer, primary_key=True, autoincrement=True)
    day = Column(Enum("Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", name="day_of_week"), nullable=False, unique=True)
