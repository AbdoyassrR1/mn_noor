#!/usr/bin/python3
from app.models.base import BaseModel
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import relationship


class Role(BaseModel):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(10), nullable=False, unique=True)
    description = Column(Text, nullable=False)

    users = relationship("User", backref="role")

    def __repr__(self):
        return f"<Role ID: {self.id}, Role Name: {self.role}>"

    # Convert to dictionary for API response
    def to_dict(self):
        TIME = "%a, %d %b %Y %I:%M:%S %p"
        return {
            "id": self.id,
            "name": self.role,
            "description": self.description,
            "created_at": self.created_at.strftime(TIME),
            "updated_at": self.updated_at.strftime(TIME)
        }
