#!/usr/bin/python3
from app.app import db
from sqlalchemy import Column, Integer, ForeignKey, Time
from sqlalchemy.orm import relationship


class GroupDay(db.Model):
    __tablename__ = "group_days"

    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    day_id = Column(Integer, ForeignKey("days.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    time = Column(Time, nullable=False)

    # Relationship back to Group
    group = relationship("Group", back_populates="group_days", overlaps="days, groups")

    # Relationship back to Day
    day = relationship("Day", overlaps="groups, days")

    def __repr__(self):
        return f"<GroupDay(group_id={self.group_id}, day_id={self.day_id}, time={self.time})>"
