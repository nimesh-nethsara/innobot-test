# from datetime import datetime, timedelta
# from flask import Blueprint, request, jsonify
# from app.models.doctor import DoctorProfile, DoctorAvailability
# from app.models.appointment import Appointment, AppointmentStatus
# from app.utils.errors import APIError

# doctors_bp = Blueprint("doctors", __name__, url_prefix="/api/doctors")

# @doctors_bp.route("", methods=["GET"])
# def search_doctors():
#     specialty = request.args.get("specialty")
#     query = DoctorProfile.query

#     if specialty:
#         query = query.filter(DoctorProfile.specialty.ilike(f"%{specialty}%"))

#     doctors = query.all()
#     results = [{
#         "id": d.id,
#         "name": d.user.full_name,
#         "specialty": d.specialty,
#         "bio": d.bio,
#         "consultation_fee": float(d.consultation_fee)
#     } for d in doctors]

#     return jsonify({"doctors": results}), 200

# @doctors_bp.route("/<int:doctor_id>/available-slots", methods=["GET"])
# def get_available_slots(doctor_id):
#     date_str = request.args.get("date")
#     if not date_str:
#         raise APIError("Query parameter 'date' (YYYY-MM-DD) is required", 400)

#     try:
#         target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
#     except ValueError:
#         raise APIError("Invalid date format. Use YYYY-MM-DD", 400)

#     day_of_week = target_date.weekday()  # Mon=0, Sun=6
#     shifts = DoctorAvailability.query.filter_by(doctor_id=doctor_id, day_of_week=day_of_week).all()

#     # Get booked slots for this doctor on this day
#     booked_appointments = Appointment.query.filter_by(
#         doctor_id=doctor_id,
#         appointment_date=target_date,
#         status=AppointmentStatus.BOOKED
#     ).all()
#     booked_times = {a.start_time for a in booked_appointments}

#     available_slots = []
#     now = datetime.now()

#     for shift in shifts:
#         current_time = datetime.combine(target_date, shift.start_time)
#         end_time = datetime.combine(target_date, shift.end_time)
#         slot_delta = timedelta(minutes=shift.slot_duration_mins)

#         while current_time + slot_delta <= end_time:
#             slot_start = current_time.time()
#             # Edge case protection: Do not include slots that are in the past
#             if current_time > now and slot_start not in booked_times:
#                 available_slots.append({
#                     "start_time": slot_start.strftime("%H:%M"),
#                     "end_time": (current_time + slot_delta).strftime("%H:%M")
#                 })
#             current_time += slot_delta

#     return jsonify({"doctor_id": doctor_id, "date": date_str, "slots": available_slots}), 200


from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.doctor import DoctorProfile, DoctorAvailability
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User, UserRole
from app.utils.errors import APIError

doctors_bp = Blueprint("doctors", __name__, url_prefix="/api/doctors")

def get_current_user_from_header():
    """Helper utility to extract and validate user from request header."""
    user_id_str = request.headers.get("X-User-Id")
    if not user_id_str or not user_id_str.isdigit():
        raise APIError("Unauthorized: Missing or invalid 'X-User-Id' header", 401)
    
    user = User.query.get(int(user_id_str))
    if not user:
        raise APIError("Unauthorized: User does not exist", 401)
    return user

# ---------------------------------------------------------
# NEW: Doctor Availability Management Endpoints
# ---------------------------------------------------------

@doctors_bp.route("/availability", methods=["POST"])
def add_availability():
    current_user = get_current_user_from_header()
    
    if current_user.role != UserRole.DOCTOR:
        raise APIError("Forbidden: Only doctors can manage availability", 403)
        
    profile = DoctorProfile.query.filter_by(user_id=current_user.id).first_or_404()
    data = request.get_json() or {}
    
    day_of_week = data.get("day_of_week") # 0 = Monday, 6 = Sunday
    start_time_str = data.get("start_time")
    end_time_str = data.get("end_time")
    slot_duration = data.get("slot_duration_mins", 30)
    
    if day_of_week is None or not start_time_str or not end_time_str:
        raise APIError("Missing fields: day_of_week, start_time, end_time", 400)
        
    try:
        start_t = datetime.strptime(start_time_str, "%H:%M").time()
        end_t = datetime.strptime(end_time_str, "%H:%M").time()
    except ValueError:
        raise APIError("Invalid time format. Use HH:MM", 400)
        
    if start_t >= end_t:
        raise APIError("start_time must be before end_time", 400)
        
    availability = DoctorAvailability(
        doctor_id=profile.id,
        day_of_week=int(day_of_week),
        start_time=start_t,
        end_time=end_t,
        slot_duration_mins=int(slot_duration)
    )
    
    db.session.add(availability)
    db.session.commit()
    
    return jsonify({"message": "Availability added successfully", "id": availability.id}), 201

@doctors_bp.route("/availability/my", methods=["GET"])
def get_my_availability():
    current_user = get_current_user_from_header()
    
    if current_user.role != UserRole.DOCTOR:
        raise APIError("Forbidden: Only doctors can view their schedule templates", 403)
        
    profile = DoctorProfile.query.filter_by(user_id=current_user.id).first_or_404()
    shifts = DoctorAvailability.query.filter_by(doctor_id=profile.id).order_by(DoctorAvailability.day_of_week).all()
    
    # Map integers back to day names for frontend convenience
    days_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    
    results = [{
        "id": s.id,
        "day_of_week": s.day_of_week,
        "day_name": days_map.get(s.day_of_week),
        "start_time": s.start_time.strftime("%H:%M"),
        "end_time": s.end_time.strftime("%H:%M"),
        "slot_duration_mins": s.slot_duration_mins
    } for s in shifts]
    
    return jsonify({"availability": results}), 200

# ---------------------------------------------------------
# EXISTING: Search and Available Slots Endpoints
# ---------------------------------------------------------

@doctors_bp.route("", methods=["GET"])
@doctors_bp.route("", methods=["GET"])
def search_doctors():
    # Changed from 'specialty' to a general 'search' parameter
    search_term = request.args.get("search")
    
    # We must join the User table to access the doctor's full_name
    query = DoctorProfile.query.join(User)

    if search_term:
        query = query.filter(
            db.or_(
                DoctorProfile.specialty.ilike(f"%{search_term}%"),
                User.full_name.ilike(f"%{search_term}%")
            )
        )

    doctors = query.all()
    results = [{
        "id": d.id,
        "name": d.user.full_name,
        "specialty": d.specialty,
        "bio": d.bio,
        "consultation_fee": float(d.consultation_fee)
    } for d in doctors]

    return jsonify({"doctors": results}), 200

# def search_doctors():
#     specialty = request.args.get("specialty")
#     query = DoctorProfile.query

#     if specialty:
#         query = query.filter(DoctorProfile.specialty.ilike(f"%{specialty}%"))

#     doctors = query.all()
#     results = [{
#         "id": d.id,
#         "name": d.user.full_name,
#         "specialty": d.specialty,
#         "bio": d.bio,
#         "consultation_fee": float(d.consultation_fee)
#     } for d in doctors]

#     return jsonify({"doctors": results}), 200

@doctors_bp.route("/<int:doctor_id>/available-slots", methods=["GET"])
def get_available_slots(doctor_id):
    date_str = request.args.get("date")
    if not date_str:
        raise APIError("Query parameter 'date' (YYYY-MM-DD) is required", 400)

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise APIError("Invalid date format. Use YYYY-MM-DD", 400)

    day_of_week = target_date.weekday()  # Mon=0, Sun=6
    shifts = DoctorAvailability.query.filter_by(doctor_id=doctor_id, day_of_week=day_of_week).all()

    # Get booked slots for this doctor on this day
    booked_appointments = Appointment.query.filter_by(
        doctor_id=doctor_id,
        appointment_date=target_date,
        status=AppointmentStatus.BOOKED
    ).all()
    booked_times = {a.start_time for a in booked_appointments}

    available_slots = []
    now = datetime.now()

    for shift in shifts:
        current_time = datetime.combine(target_date, shift.start_time)
        end_time = datetime.combine(target_date, shift.end_time)
        slot_delta = timedelta(minutes=shift.slot_duration_mins)

        while current_time + slot_delta <= end_time:
            slot_start = current_time.time()
            # Edge case protection: Do not include slots that are in the past
            if current_time > now and slot_start not in booked_times:
                available_slots.append({
                    "start_time": slot_start.strftime("%H:%M"),
                    "end_time": (current_time + slot_delta).strftime("%H:%M")
                })
            current_time += slot_delta

    return jsonify({"doctor_id": doctor_id, "date": date_str, "slots": available_slots}), 200