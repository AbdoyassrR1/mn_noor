#!/usr/bin/python3
from flask import Blueprint, request, jsonify, abort
from flask_login import logout_user, login_required, current_user
import re
from app.models.user import User
from app.models.language import Language
from app.app import db


profile = Blueprint("profile", __name__)


# Protected profile route
@profile.route("/", strict_slashes=False)
@login_required
def get_profile():
    """ get the logged in user profile """
    return jsonify(current_user.to_dict()), 200


# Protected profile update route
@profile.route("/update_profile", methods=["PATCH"])
@login_required
def update_profile():
    """ Update the logged in user data """
    updated_data = request.get_json()

    allowed_fields = ["first_name", "last_name", "password",
                      "photo", "parent_phone_number","language",
                      "email", "phone_number"]
    is_updated = False

    for key, value in updated_data.items():
        if key in allowed_fields:

            if key == "first_name":
                # Validate first name (example: letters and spaces only, 2-30 characters)
                if not re.match(r"^[a-zA-Z\s]{2,30}$", updated_data["first_name"]) or not value:
                    abort(400, description="First name must contain only letters and spaces, and be 2 to 30 characters long")
                setattr(current_user, key, value)
                is_updated = True

            elif key == "last_name":
                # Validate last name (example: letters and spaces only, 2-30 characters)
                if not re.match(r"^[a-zA-Z\s]{2,30}$", updated_data["last_name"]) or not value:
                    abort(400, description="Last name must contain only letters and spaces, and be 2 to 30 characters long")
                setattr(current_user, key, value)
                is_updated = True

            elif key == "password":
                if "old_password" not in updated_data:
                    abort(400, description="Missing old password")
                new_password = value
                old_password = updated_data["old_password"]

                # Validate the new password (example: at least 8 characters)
                if len(new_password) < 8:
                    abort(400, description="Password must be at least 8 characters long")

                # check the old password
                if not current_user.check_password(old_password):
                    abort(401, description="Incorrect old password")

                current_user.set_password(new_password)
                is_updated = True
                logout_user()
            
            elif key == "language":
                language = Language.query.filter_by(language=value).first()
                if not language:
                    abort(500, description="Language not found in the database")
                current_user.language_id = language.id
                is_updated = True


    if not is_updated:
        return jsonify({
            "status": "error",
            "message": "No Changes Made"
        }), 400

    # Commit the changes to the database
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Profile Updated Successfully"
    }), 200


@profile.route("/delete_account", methods=["DELETE"])
@login_required
def delete_account():
    """ Delete the logged in user account """
    data = request.get_json()

    required_fields = ["password"]

    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        abort(400, description=f"Missing fields: {', '.join(missing_fields)}")

    password = data["password"]

    # confirm password before deletion for more security
    if not password:
        abort(400, description="Confirming the Password is Required")
    if not current_user.check_password(password):
        abort(400, description="Incorrect password")

    db.session.delete(current_user)
    db.session.commit()
    logout_user()

    return jsonify({
        "status": "success",
        "message": "User Account Deleted Successfully"
    }), 200
