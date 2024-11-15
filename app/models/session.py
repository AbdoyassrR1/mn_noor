#!/usr/bin/python3
from app.app import db, local_timezone
from app.models.user import User
from datetime import datetime, timedelta
from sqlalchemy import Column, DateTime, Integer, Enum, Time, Float, ForeignKey, String


class Session(db.Model):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=lambda: datetime.now(local_timezone))
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    length = Column(Float, nullable=False)
    type = Column(Enum("private", "group", name="session_type"), nullable=False)

    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # check_role_teacher
    #     teacher = User.query.filter_by(id=self.user_id).first()
    #     if teacher is None:
    #         raise ValueError("User not found")
    #     if teacher.role.role != "teacher":
    #         raise ValueError("A session must created by teacher only")
    #     self.users.append(teacher)

    def set_length(self):
        session_length = timedelta(
            hours=self.end_time.hour - self.start_time.hour,
            minutes=self.end_time.minute - self.start_time.minute,
            seconds=self.end_time.second - self.start_time.second
        )
        self.length = session_length.total_seconds() / 60  # in minutes
