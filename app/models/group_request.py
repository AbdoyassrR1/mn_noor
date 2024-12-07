#!/user/bin/python3
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class GroupRequest(BaseModel):
    __tablename__ = "group_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    action = Column(Enum("join", "leave", name="request_action"), nullable=False)
    role = Column(Enum("student", "teacher", "admin", name="request_role"), nullable=False)
    status = Column(Enum("pending", "approved", "rejected", name="request_status"), nullable=False, default="pending")
    note = Column(Text, nullable=True)  # Optional note for request

    def __repr__(self):
        return f"<Request ID: {self.id} user_id={self.user_id}, group_id={self.group_id}, role={self.role}, status={self.status}>"

    # Convert to dictionary for API response
    def to_dict(self):
        TIME = "%a, %d %b %Y %I:%M:%S %p"
        return {
            "id": self.id,
            "user_id": self.user_id,
            "group_id": self.group_id,
            "role": self.role,
            "status": self.status,
            "action": self.action,
            "note": self.note,
            "created_at": self.created_at.strftime(TIME),
            "updated_at": self.updated_at.strftime(TIME)
        }
