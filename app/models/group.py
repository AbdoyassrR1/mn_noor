#!/usr/bin/python3
from app.models.base import BaseModel
from sqlalchemy import Column, String, Integer, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship

class Group(BaseModel):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group = Column(String(50), nullable=False, unique=True)
    size = Column(Integer, nullable=False)
    status = Column(Enum("coming", "running", "finished", name='group_status'), nullable=False, default="coming")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    teacher_id = Column(String(50), ForeignKey("users.id"), nullable=True)

    group_days = relationship("GroupDay", back_populates="group", cascade="all, delete-orphan", passive_deletes=True, overlaps="days")

    # # many-to-many relationship
    days = relationship("Day", secondary="group_days", back_populates="groups", overlaps="group_days")
    group_requests = relationship("User", secondary="group_requests",backref="group_requests")

    def __repr__(self):
        return f"<group: {self.group}, size: {self.size}, status: {self.status}>"


    # Convert to dictionary for API response
    def to_dict(self):
        TIME = "%a, %d %b %Y %I:%M:%S %p"
        TIME_WITH_AMPM = "%I:%M:%S %p"

        days_with_time = [
            {
                "id": day.id,
                "day": day.day,
                "time": group_day.time.strftime(TIME_WITH_AMPM)  # Format time with AM/PM
            }
            for day, group_day in zip(self.days, self.group_days)  # Pair days with group_days
        ]

        return {
            "id": self.id,
            "group": self.group,
            "size": self.size,
            "days": days_with_time,
            "days_per_week": len(days_with_time),
            "status": self.status,
            "start_date": self.start_date.strftime(TIME),
            "end_date": self.end_date.strftime(TIME),
            "created_at": self.created_at.strftime(TIME),
            "updated_at": self.updated_at.strftime(TIME),
        }
