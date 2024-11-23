#!/usr/bin/python3
from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from datetime import datetime
import re
from app.app import db, limiter
from app.models.group import Group
from app.models.user import User
from app.models.day import Day
from app.models.group_day import GroupDay


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


@groups.route("/create_group", methods=["POST"])
@login_required  # Ensure the user is logged in
@limiter.limit("5/minute")  # Rate limit to prevent abuse
def create_group():
    # Get the current logged-in user
    user = User.query.filter_by(id=current_user.id).first()

    if not user:
        abort(404, description="User not found")

    # Check if the user is an admin
    if user.role.role != "admin":
        abort(403, description="Only admins can create groups.")

    # Parse request data
    group_data = request.get_json()

    required_fields = ["group", "size", "day_ids", "start_date", "end_date"]

    # Check for missing fields
    missing_fields = [field for field in required_fields if field not in group_data]
    if missing_fields:
        abort(400, description=f"Missing fields: {', '.join(missing_fields)}")
    
    # Check for empty fields
    empty_fields = [field for field in required_fields if not group_data[field]]
    if empty_fields:
        abort(400, description=f"Empty fields: {', '.join(empty_fields)}")

    # Check uniqueness of the group name
    if Group.query.filter_by(group=group_data["group"]).first():
        abort(409, description="Group name already exists.")

    # Validate group name
    if not re.match(r"^[a-zA-Z0-9_\-\s]{2,100}$", group_data["group"]):
        abort(400, description="Group name must be 2-100 characters long and can include letters, numbers, spaces, underscores, and hyphens.")

    
    # Validate date format
    try:
        start_date = datetime.strptime(group_data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(group_data["end_date"], "%Y-%m-%d").date()
    except ValueError:
        abort(400, description="Invalid date format. Use YYYY-MM-DD")
    
    if start_date >= end_date:
        abort(400, description="End date must be after start date.")

    # Validate `status` field
    valid_statuses = ["coming", "running", "finished"]
    status= ""
    date_now = datetime.strptime(str(datetime.today().date()), "%Y-%m-%d").date()

    if start_date > date_now:
        status = "coming"
    elif start_date <= date_now and end_date >= date_now:
        status = "running"
    else:
        status = "finished"

    # validate size 
    if type(group_data["size"]) is not int or group_data["size"] <= 0:
        abort(400, description="Size Must be a number starting from 1.")

    # validate days and times

    day_ids_with_times  = group_data["day_ids"]

    if not day_ids_with_times or not isinstance(day_ids_with_times , list) or not all(
        isinstance(entry, dict) and "day_id" in entry and "time" in entry for entry in day_ids_with_times ):
        abort(400, description="day_ids must be a list of objects with 'day_id' and 'time'.")

    day_ids = [entry["day_id"] for entry in day_ids_with_times]

    valid_days = Day.query.filter(Day.id.in_([day_id for day_id in day_ids])).all()

    # Check if all provided day IDs are valid
    valid_day_ids = {day.id for day in valid_days}
    invalid_day_ids = [day_id for day_id in day_ids if day_id not in valid_day_ids]

    if invalid_day_ids:
        abort(400, description=f"Invalid day IDs provided: {', '.join(invalid_day_ids)}")

    if len(day_ids) != len(set(day_ids)):
        abort(400, description="duplicate day IDs provided.")
    
    # Validate times
    for entry in day_ids_with_times:
        try:
            # Validate and convert time to 24-hour format
            time_24_hour = datetime.strptime(entry["time"], "%I:%M:%S %p").strftime("%H:%M:%S")
            entry["time"] = time_24_hour
        except ValueError:
            abort(400, description=f"Invalid time format for day_id {entry['day_id']}. Use HH:MM:SS AM/PM.")


    # Create new Group instance
    new_group = Group(
        group=group_data["group"],
        size=group_data["size"],
        start_date=start_date,
        end_date=end_date,
        status=status
    )

    # Save to the database
    db.session.add(new_group)
    db.session.flush()  # Ensures new_group.id is available before commit


    # Create associated GroupDay entries
    group_days = [
    GroupDay(group_id=new_group.id, day_id=entry["day_id"], time=entry["time"])
    for entry in day_ids_with_times
    ]

    db.session.add_all(group_days)
    db.session.commit()


    return jsonify({
        "status": "success",
        "message": "Group Has Been Created Successfully.",
        "group": new_group.to_dict()
        }), 201
