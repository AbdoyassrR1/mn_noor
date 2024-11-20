#!/usr/bin/python3
from app.models.base import BaseModel
from sqlalchemy import Column, String, Integer, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship

class Group(BaseModel):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group = Column(String(50), nullable=False, unique=True)
    size = Column(Integer, nullable=False)
    days = Column(String(30), nullable=False)
    status = Column(Enum("coming", "running", "finished", name='group_status'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    teacher_id = Column(String(50), ForeignKey("users.id"), nullable=True)

    # # many-to-many relationship
    days = relationship("Day", secondary="group_days", backref="groups")

    def __repr__(self):
        return f"<group: {self.group}, size: {self.size}, status: {self.status}>",


    # Convert to dictionary for API response
    def to_dict(self):
        TIME = "%a, %d %b %Y %I:%M:%S %p"
        return {
            "id": self.id,
            "group": self.group,
            "size": self.size,
            "days": self.days,
            "status": self.status,
            "start_date": self.start_date.strftime(TIME),
            "end_date": self.end_date.strftime(TIME),
            "created_at": self.created_at.strftime(TIME),
            "updated_at": self.updated_at.strftime(TIME),
        }
