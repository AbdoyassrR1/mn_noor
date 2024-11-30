#!/usr/bin/python3
from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from datetime import datetime
import re
from sqlalchemy.orm import joinedload
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
    user = User.query.get(current_user.id)
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
    user = User.query.get(current_user.id)

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
    if not isinstance(group_data["group"], str) or not re.match(r"^[a-zA-Z0-9_\-\s]{2,100}$", group_data["group"]):
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
    status= ""
    date_now = datetime.strptime(str(datetime.today().date()), "%Y-%m-%d").date()

    if start_date > date_now:
        status = "coming"
    elif start_date <= date_now and end_date >= date_now:
        status = "running"
    elif date_now > end_date:
        status = "finished"

    # validate size 
    if type(group_data["size"]) is not int or group_data["size"] <= 0:
        abort(400, description="Size must be an integer greater than 0.")

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



@groups.route("/update_group/<int:group_id>", methods=["PATCH"])
@login_required  # Ensure the user is logged in
def update_group(group_id):

    # Get the current logged-in user
    user = User.query.get(current_user.id)
    if not user:
        abort(404, description="User not found")

    # Check if the user is an admin
    if user.role.role != "admin":
        abort(403, description="Only admins can update groups.")
    
    group_to_update = Group.query.get(group_id)

    if not group_to_update:
        abort(404, description="Group not Found")

    updated_data = request.get_json() 

    allowed_fields = ["group", "size", "start_date",
                      "end_date", "day_ids"]

    is_updated = False

    for key, value in updated_data.items():
        if key in allowed_fields:

            if key == "group":
                # Check uniqueness of the group name
                if Group.query.filter(Group.group == value, Group.id != group_to_update.id).first():
                    abort(409, description="Group name already exists.")
                # Validate group name
                if not isinstance(value, str) or not re.match(r"^[a-zA-Z0-9_\-\s]{2,100}$", value):
                    abort(400, description="Group name must be 2-100 characters long and can include letters, numbers, spaces, underscores, and hyphens.")
                setattr(group_to_update, key, value)
                is_updated = True
            
            if key == "size":
                # validate size 
                if type(value) is not int or value <= 0:
                    abort(400, description="Size must be an integer greater than 0.")
                setattr(group_to_update, key, value)
                is_updated = True

            if key == "start_date":
                # Validate date format
                try:
                    start_date = datetime.strptime(value, "%Y-%m-%d").date()
                except ValueError:
                    abort(400, description="Invalid date format. Use YYYY-MM-DD")

                if start_date >= group_to_update.end_date:
                    abort(400, description="End date must be after start date.")

                setattr(group_to_update, key, start_date)

                # Validate `status` field
                status= ""
                date_now = datetime.strptime(str(datetime.today().date()), "%Y-%m-%d").date()

                if start_date > date_now:
                    status = "coming"
                elif start_date <= date_now and group_to_update.end_date >= date_now:
                    status = "running"
                elif date_now > group_to_update.end_date:
                    status = "finished"

                group_to_update.status = status

                is_updated = True

            if key == "end_date":
                # Validate date format
                try:
                    end_date = datetime.strptime(value, "%Y-%m-%d").date()
                except ValueError:
                    abort(400, description="Invalid date format. Use YYYY-MM-DD")

                if group_to_update.start_date >= end_date:
                    abort(400, description="End date must be after start date.")

                setattr(group_to_update, key, end_date)

                # Validate `status` field
                status= ""
                date_now = datetime.strptime(str(datetime.today().date()), "%Y-%m-%d").date()

                if group_to_update.start_date > date_now:
                    status = "coming"
                elif group_to_update.start_date <= date_now and end_date >= date_now:
                    status = "running"
                elif date_now > end_date:
                    status = "finished"

                group_to_update.status = status

                is_updated = True

            if key == "day_ids":
                # validate days and times

                day_ids_with_times  = updated_data[key]

                if not day_ids_with_times or not  isinstance(day_ids_with_times , list) or not all(
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
                
                # update associated GroupDay entries
                existing_group_days = {group_day.day_id: group_day for group_day in group_to_update.group_days}
                # Update or create new GroupDay entries
                for entry in day_ids_with_times:
                    day_id = entry["day_id"]
                    time = entry["time"]

                    if day_id in existing_group_days:
                        # Update existing entry
                        existing_group_days[day_id].time = time
                    else:
                        # Create new entry
                        new_group_day = GroupDay(group_id=group_to_update.id, day_id=day_id, time=time)
                        db.session.add(new_group_day)

                # Remove unused GroupDay entries
                current_day_ids = {entry["day_id"] for entry in day_ids_with_times}
                for day_id, group_day in existing_group_days.items():
                    if day_id not in current_day_ids:
                        db.session.delete(group_day)

                is_updated = True


    # If no changes were made, return an error
    if not is_updated:
        abort(400, description="No valid fields to update or no changes made")

    # Commit the changes to the database
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Group Has Been Updated Successfully.",
        "group": group_to_update.to_dict()
    }), 200




@groups.route("/delete_group/<int:group_id>", methods=["DELETE"])
@login_required  # Ensure the user is logged in
@limiter.limit("5/minute")
def delete_group(group_id):

    # Get the current logged-in user
    user = User.query.get(current_user.id)
    if not user:
        abort(404, description="User not found")

    # Check if the user is an admin
    if user.role.role != "admin":
        abort(403, description="Only admins can delete groups.")
    
    group_to_delete = Group.query.get(group_id)

    if not group_to_delete:
        abort(404, description="Group not Found")
    
    db.session.delete(group_to_delete)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": f"Group with ID: {group_to_delete.id} Has Been Deleted Successfully."
    }), 200


@groups.route("/add_student_to_group/<int:group_id>/<student_id>", methods=["POST"])
@login_required  # Ensure the user is logged in
@limiter.limit("10/minute")
def add_student_to_group(group_id, student_id):

    # Get the current logged-in user
    # user = User.query.get(current_user.id)
    user = current_user
    if not user:
        abort(404, description="User not found")

    # Check if the user is an admin
    if user.role.role != "admin":
        abort(403, description="Only admins can add students to groups.")
    
    # check if the group is exists
    group_to_join = Group.query.get(group_id)
    if not group_to_join:
        abort(404, description=f"Group with ID: {group_id} not Found")

    # check if the student is exists
    student_to_add = User.query.get(student_id)
    if not student_to_add:
        abort(404, description=f"Student with ID: {student_id} not Found")

    # Check student role
    if student_to_add.role.role != "student":
        abort(403, description="Only students can be added to groups.")

    # check if the student already in the group
    if student_to_add in group_to_join.users:
        abort(409, description=f"Student: ({student_to_add.username}) is already a member of this group.")

    # Check if the group has space for more students
    if len(group_to_join.users) >= group_to_join.size:
        abort(400, description="Group capacity has been reached.")

    group_to_join.users.append(student_to_add)
    db.session.commit()


    return jsonify({
        "status": "success",
        "message": f"Student ({student_to_add.username}) has been added to group ({group_to_join.group}).",
        "group": {
            "id": group_to_join.id,
            "name": group_to_join.group,
            "remaining_capacity": group_to_join.size - len(group_to_join.users),
            "students": [{"id": user.id, "username": user.username} for user in group_to_join.users]
        }
    }), 200


@groups.route("/get_student_list_of_group/<int:group_id>/", methods=["GET"])
@login_required  # Ensure the user is logged in
def get_student_list_of_group(group_id):

    # Get the current logged-in user
    user = current_user
    if not user:
        abort(404, description="User not found")

    # Check if the user is an admin
    if user.role.role != "admin":
        abort(403, description="Only admins can view students list of groups.")
    
    # check if the group is exists
    # group_to_view = Group.query.get(group_id) # inefficient way query for each uesr in the list
    group_to_view = Group.query.options(joinedload(Group.users)).get(group_id) # query one time for the group and uesrs in the list
    if not group_to_view:
        abort(404, description=f"Group with ID: {group_id} not Found")

    return jsonify({
        "status": "success",
        "message": f"Student list has been retrieved for group: ({group_to_view.group}).",
        "group": {
            "id": group_to_view.id,
            "name": group_to_view.group,
            "status": group_to_view.status,
            "remaining_capacity": group_to_view.size - len(group_to_view.users),
            "total_students": len(group_to_view.users),
            "students": [{"id": user.id, "username": user.username} for user in group_to_view.users]
        }
    }), 200
