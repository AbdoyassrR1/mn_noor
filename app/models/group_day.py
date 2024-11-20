#!/usr/bin/python3
from app.app import db
from sqlalchemy import Column, Integer, ForeignKey, Time 


class GroupDay(db.Model):
    __tablename__ = "user_groups"

    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False, primary_key=True)
    day_id = Column(Integer, ForeignKey("users.id"), nullable=False, primary_key=True)
    time = Column(Time, nullable=False)
