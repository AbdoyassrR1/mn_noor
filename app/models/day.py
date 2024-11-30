#!/usr/bin/python3
from app.app import db
from sqlalchemy import Column, Integer, Enum
from sqlalchemy.orm import relationship

class Day(db.Model):
    __tablename__ = "days"

    id = Column(Integer, primary_key=True, autoincrement=True)
    day = Column(Enum("Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", name="day_of_week"), nullable=False, unique=True)

    groups = relationship("Group", secondary="group_days", back_populates="days", overlaps="group_days")

    def __repr__(self):
        return f"<Day(day={self.day})>"
