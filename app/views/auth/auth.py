#!/usr/bin/python3
from flask import Blueprint, jsonify, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import re
from app.app import db, limiter
from app.models.user import User
from app.models.role import Role
from app.models.language import Language

auth = Blueprint("auth", __name__)

# Teacher Registration route
@auth.route("/register_teacher", methods=["POST"])
@limiter.limit("5/minute")
def register_teacher():
    # Retrieve data from the request body as JSON
    user_data = request.get_json()

    if not user_data:
        abort(400, description="Missing JSON object")


    # Required fields for a teacher registration
    required_fields = ["username", "email", "password", "phone_number", "first_name",
                       "last_name", "birth_date", "gender", "nationality", "country",
                       "time_zone", "national_id", "language"]

    # Check for missing fields
    missing_fields = [field for field in required_fields if field not in user_data]
    if missing_fields:
        abort(400, description=f"Missing fields: {', '.join(missing_fields)}")

    # Check for empty fields
    empty_fields = [field for field in required_fields if not user_data[field]]
    if empty_fields:
        abort(400, description=f"Empty fields: {', '.join(empty_fields)}")

    # Validate username (example: alphanumeric, 3-20 characters)
    if not re.match("^[a-zA-Z0-9_]{3,20}$", user_data["username"]):
        abort(400, description="Invalid username format")

    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", user_data["email"]):
        abort(400, description="Invalid email format")

    # Validate first name (example: letters and spaces only, 2-30 characters)
    if not re.match(r"^[a-zA-Z\s]{2,30}$", user_data["first_name"]):
        abort(400, description="First name must contain only letters and spaces, and be 2 to 30 characters long")

    # Validate last name (example: letters and spaces only, 2-30 characters)
    if not re.match(r"^[a-zA-Z\s]{2,30}$", user_data["last_name"]):
        abort(400, description="Last name must contain only letters and spaces, and be 2 to 30 characters long")

    # Validate password (example: at least 8 characters)
    if len(user_data["password"]) < 8:
        abort(400, description="Password must be at least 8 characters long")

    # Validate phone number (example: numeric and 10-15 digits)
    if not re.match(r"^\+?\d{10,15}$", user_data["phone_number"]):
        abort(400, description="Invalid phone number format")

    # Validate birth date (example: format and age check)
    try:
        birth_date = datetime.strptime(user_data["birth_date"], "%Y-%m-%d").date()
        # age = (datetime.now().date() - birth_date).days // 365
        # if age < 18:
        #     abort(400, description="User must be at least 18 years old")
    except ValueError:
        abort(400, description="Invalid birth date format. Use YYYY-MM-DD")

    # Validate gender
    if user_data["gender"] not in ["MALE", "FEMALE"]:
        abort(400, description="Invalid gender value")

    # Validate nationality (example: letters only)
    if not re.match(r"^[a-zA-Z\s]+$", user_data["nationality"]):
        abort(400, description="Nationality must contain only letters and spaces")
    
    # Validate country (example: letters only)
    if not re.match(r"^[a-zA-Z\s]+$", user_data["country"]):
        abort(400, description="Country must contain only letters and spaces")

    # Validate national ID (example: alphanumeric, customize as needed)
    if not re.match(r"^[a-zA-Z0-9]{5,20}$", user_data["national_id"]):
        abort(400, description="Invalid national ID format")

    # Check uniqueness of the username, email and phone number
    if User.query.filter_by(username=user_data["username"]).first():
        abort(409, description="Username already exists")
    if User.query.filter_by(email=user_data["email"]).first():
        abort(409, description="Email already exists")
    if User.query.filter_by(phone_number=user_data["phone_number"]).first():
        abort(409, description="Phone number already exists")

    # Retrieve the teacher role from the database
    teacher_role = Role.query.filter_by(role="teacher").first()
    if not teacher_role:
        abort(500, description="Teacher role not found in the database")

    # Retrieve the language from the database
    language = Language.query.filter_by(language=user_data["language"]).first()
    if not language:
        abort(500, description="language not found in the database")

    # Create a new user instance with the data
    new_user = User(
        username=user_data["username"],
        email=user_data["email"],
        phone_number=user_data["phone_number"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        birth_date=birth_date,
        gender=user_data["gender"],
        nationality=user_data["nationality"],
        country=user_data["country"],
        time_zone=user_data["time_zone"],
        national_id=user_data["national_id"],
        role_id=teacher_role.id,
        language_id=language.id
    )
    new_user.set_password(user_data["password"])

    # Add and commit the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # Log the user in automatically
    login_user(new_user)

    # Return a success response with the user data
    return jsonify({
        "status": "success",
        "user": {
            "username": new_user.username,
            "email": new_user.email
        },
        "message": "Teacher account created and logged in successfully"
    }), 201


# Student Registration route
@auth.route("/register_student", methods=["POST"])
@limiter.limit("5/minute")
def register_student():
    # Retrieve data from the request body as JSON
    user_data = request.get_json()

    if not user_data:
        abort(400, description="Missing JSON object")

    # Required fields for a Student registration
    required_fields = ["username", "email", "password", "phone_number", "first_name",
                       "last_name", "birth_date", "gender", "nationality", "country",
                       "time_zone", "level", "language", "parent_phone_number"]

    # Check for missing fields
    missing_fields = [field for field in required_fields if field not in user_data]
    if missing_fields:
        abort(400, description=f"Missing fields: {', '.join(missing_fields)}")

    # Check for empty fields
    empty_fields = [field for field in required_fields if not user_data[field]]
    if empty_fields:
        abort(400, description=f"Empty fields: {', '.join(empty_fields)}")

    # Validate username (example: alphanumeric, 3-20 characters)
    if not re.match("^[a-zA-Z0-9_]{3,20}$", user_data["username"]):
        abort(400, description="Invalid username format")

    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", user_data["email"]):
        abort(400, description="Invalid email format")

    # Validate password (example: at least 8 characters)
    if len(user_data["password"]) < 8:
        abort(400, description="Password must be at least 8 characters long")

    # Validate phone number (example: numeric and 10-15 digits)
    if not re.match(r"^\+?\d{10,15}$", user_data["phone_number"]):
        abort(400, description="Invalid phone number format")

    # Validate parent phone number (example: numeric and 10-15 digits)
    if not re.match(r"^\+?\d{10,15}$", user_data["parent_phone_number"]):
        abort(400, description="Invalid phone number format")

    # Validate birth date (example: format and age check)
    try:
        birth_date = datetime.strptime(user_data["birth_date"], "%Y-%m-%d").date()
        # age = (datetime.now().date() - birth_date).days // 365
        # if age < 18:
        #     abort(400, description="User must be at least 18 years old")
    except ValueError:
        abort(400, description="Invalid birth date format. Use YYYY-MM-DD")

    # Validate gender
    if user_data["gender"] not in ["MALE", "FEMALE"]:
        abort(400, description="Invalid gender value")

    # Validate nationality (example: letters only)
    if not re.match(r"^[a-zA-Z\s]+$", user_data["nationality"]):
        abort(400, description="Nationality must contain only letters and spaces")

    # Validate country (example: letters only)
    if not re.match(r"^[a-zA-Z\s]+$", user_data["country"]):
        abort(400, description="Country must contain only letters and spaces")

    try:
        level = int(user_data["level"])
    except ValueError:
        abort(400, description="level Must be an Integer.")

    # Check uniqueness of the username, email and phone number
    if User.query.filter_by(username=user_data["username"]).first():
        abort(409, description="Username already exists")
    if User.query.filter_by(email=user_data["email"]).first():
        abort(409, description="Email already exists")
    if User.query.filter_by(phone_number=user_data["phone_number"]).first():
        abort(409, description="Phone number already exists")

    # Retrieve the student role from the database
    student_role = Role.query.filter_by(role="student").first()
    if not student_role:
        abort(500, description="Student role not found in the database")

    # Retrieve the language from the database
    language = Language.query.filter_by(language=user_data["language"]).first()
    if not language:
        abort(500, description="language not found in the database")

    # Create a new user instance with the data
    new_user = User(
        username=user_data["username"],
        email=user_data["email"],
        phone_number=user_data["phone_number"],
        parent_phone_number=user_data["parent_phone_number"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        birth_date=birth_date,
        gender=user_data["gender"],
        nationality=user_data["nationality"],
        country=user_data["country"],
        time_zone=user_data["time_zone"],
        level=user_data["level"],
        role_id=student_role.id,
        language_id=language.id
    )
    new_user.set_password(user_data["password"])

    # Add and commit the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # Log the user in automatically
    login_user(new_user)

    # Return a success response with the user data
    return jsonify({
        "status": "success",
        "user": {
            "username": new_user.username,
            "email": new_user.email
        },
        "message": "Student account created and logged in successfully"
    }), 201


# Login route
@auth.route("/login", methods=["POST"])
@limiter.limit("5/minute")
def login():
    # check if logged in
    if current_user.is_authenticated:
        abort(400, description="You are already logged in.")
    # get user data
    user_data = request.get_json()
    if not user_data:
        abort(400, description="Missing JSON object")

    required_fields = ["email", "password"]

    # Check for missing fields
    missing_fields = [field for field in required_fields if field not in user_data]
    if missing_fields:
        abort(400, description=f"Missing fields: {', '.join(missing_fields)}")
    
    # Check for empty fields
    empty_fields = [field for field in required_fields if not user_data[field]]
    if empty_fields:
        abort(400, description=f"Empty fields: {', '.join(empty_fields)}")

    user = User.query.filter_by(email=user_data["email"]).first()

    if not user:
        abort(401, description="Invalid email")
    if not user.check_password(user_data["password"]):
        abort(401, description="Invalid password")

    remember_me = False 
    if "remember_me" in user_data:
        remember_me = user_data["remember_me"] 

    login_user(user, remember=bool(remember_me))

    return jsonify({
        "status": "success",
        "user": {
            "username": user.username,
            "email": user.email
        },
        "message": "logged in"
    }), 200


# Logout route
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({
        "status": "success",
        "message": "User logged out"
        }), 200
