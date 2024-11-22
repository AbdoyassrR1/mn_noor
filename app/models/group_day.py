#!/usr/bin/python3
from app.app import db
from sqlalchemy import Column, Integer, ForeignKey, Time 


class GroupDay(db.Model):
    __tablename__ = "group_days"

    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False, primary_key=True)
    day_id = Column(Integer, ForeignKey("days.id"), nullable=False, primary_key=True)
    time = Column(Time, nullable=False)

    def __repr__(self):
        return f"<GroupDay(group_id={self.group_id}, day_id={self.day_id}, time={self.time})>"
