#!/usr/bin/python3
from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from datetime import datetime
import re
from app.app import db, limiter
from app.models.group import Group
from app.models.user import User
from app.models.day import Day


groups = Blueprint("groups", __name__)


@groups.route("/", methods=["GET"])
@login_required  # Ensure the user is logged in
def get_groups():

    # Get the current logged-in user
    user = User.query.filter_by(id=current_user.id).first()
    if not user:
        abort(404, description="User not found")

    query = Group.query

    # handle query parameters for filtering
    search = request.args.get("search")
    status = request.args.get("status")
    size = request.args.get("size")

    # check user role
    if user.role.role == "admin":
        # admin can see all groups
        all_groups = query
    elif user.role.role == "student":
        all_groups = query.filter_by(status="coming")
    
    if search:
        all_groups = all_groups.filter(Group.group.ilike(f"%{search}%"))

    if status :
        valid_statuses = {"coming", "running", "finished"}
        if status not in valid_statuses:
            abort(400, description="Invalid status. Must be 'coming', 'running', or 'finished'.")
            
        else:
            all_groups = all_groups.filter_by(status=status)
    if size:
        try:
            all_groups = all_groups.filter_by(size=size)
        except ValueError:
            abort(400, description="Size Must be an INTEGER.")

    # handle pagination
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    paginated_groups = all_groups.paginate(page=page, per_page=per_page, error_out=False)

    # If no groups were found
    if not paginated_groups.items:
        abort(404, description="No Groups Found")

    all_groups = [group.to_dict() for group in paginated_groups.items]

    # Return the groups with pagination metadata
    return jsonify({
        "groups": all_groups,
        "total_groups": paginated_groups.total,
        "total_pages": paginated_groups.pages,
        "current_page": paginated_groups.page,
        "next_page": paginated_groups.next_num if paginated_groups.has_next else None,
        "prev_page": paginated_groups.prev_num if paginated_groups.has_prev else None,
    })
