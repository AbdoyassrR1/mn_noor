#!/usr/bin/python3
from app.models.base import BaseModel
from flask_login import UserMixin
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.app import bcrypt, local_timezone



class User(BaseModel, UserMixin):
    __tablename__ = "users"

    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False, unique=True)
    first_name = Column(String(20), nullable=False)
    last_name = Column(String(20), nullable=False)
    photo = Column(String(100), nullable=True)
    birth_date = Column(Date, nullable=False)
    gender = Column(Enum("MALE", "FEMALE", name="gender"), nullable=False)
    nationality = Column(String(15), nullable=False)
    country = Column(String(15), nullable=False)
    time_zone = Column(String(50), nullable=False)
    parent_phone_number = Column(String(20), nullable=True)
    level = Column(Integer, nullable=True)
    national_id = Column(String(30), nullable=True, unique=True)
    salary = Column(Float, nullable=True)
    privileges = Column(String(100), nullable=True)
    position = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, default=lambda: datetime.now(local_timezone), onupdate=lambda: datetime.now(local_timezone))

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)

    # one-to-many relationship
    tokens = relationship("ResetToken", backref="user")
    teach_groups = relationship("Group", backref="teacher")
    
    # many-to-many relationship
    groups = relationship("Group", secondary="user_groups", backref="users")
    sessions = relationship("Session", secondary="user_sessions", backref="users")
    packages = relationship("Package", secondary="user_packages", backref="users")

    def __repr__(self):
        return f"<Username: {self.username}, Email: {self.email}>"

    # Set the password (hashed)
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    # Check if the password is correct
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    # Convert to dictionary for API response
    def to_dict(self):
        TIME = "%a, %d %b %Y %I:%M:%S %p"
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "photo": self.photo,
            "birth_date": self.birth_date,
            "gender": self.gender,
            "nationality": self.nationality,
            "country": self.country,
            "time_zone": self.time_zone,
            "parent_phone_number": self.parent_phone_number,
            "level": self.level,
            "national_id": self.national_id,
            "salary": self.salary,
            "privileges": self.privileges,
            "position": self.position,
            "last_login": self.last_login.strftime(TIME),
            "created_at": self.created_at.strftime(TIME),
            "updated_at": self.updated_at.strftime(TIME),
            "is_active": self.is_active,
            "role": self.role.role,
            "language": self.language.language
        }
