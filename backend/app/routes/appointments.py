from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.appointment import Appointment, AppointmentStatus
from app.models.doctor import DoctorProfile
from app.models.user import User, UserRole
from app.utils.errors import APIError

appointments_bp = Blueprint("appointments", __name__, url_prefix="/api/appointments")

def get_current_user_from_header():
    """Helper utility to extract and validate user from request header."""
    user_id_str = request.headers.get("X-User-Id")
    if not user_id_str or not user_id_str.isdigit():
        raise APIError("Unauthorized: Missing or invalid 'X-User-Id' header", 401)
    
    user = User.query.get(int(user_id_str))
    if not user:
        raise APIError("Unauthorized: User does not exist", 401)
    return user

@appointments_bp.route("", methods=["POST"])
def book_appointment():
    current_user = get_current_user_from_header()
    data = request.get_json() or {}

    doctor_id = data.get("doctor_id")
    date_str = data.get("appointment_date")
    start_time_str = data.get("start_time")
    end_time_str = data.get("end_time")

    if not all([doctor_id, date_str, start_time_str, end_time_str]):
        raise APIError("Missing fields: doctor_id, appointment_date, start_time, end_time", 400)

    try:
        appt_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_t = datetime.strptime(start_time_str, "%H:%M").time()
        end_t = datetime.strptime(end_time_str, "%H:%M").time()
    except ValueError:
        raise APIError("Invalid date/time format. Use YYYY-MM-DD and HH:MM", 400)

    # Edge Case: Prevent booking past slots
    slot_datetime = datetime.combine(appt_date, start_t)
    if slot_datetime <= datetime.now():
        raise APIError("Cannot book an appointment in the past", 400)

    # Database-level concurrency lock on existing active slots
    existing = Appointment.query.with_for_update().filter_by(
        doctor_id=doctor_id,
        appointment_date=appt_date,
        start_time=start_t,
        status=AppointmentStatus.BOOKED
    ).first()

    if existing:
        raise APIError("This time slot is already booked", 409)

    appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=doctor_id,
        appointment_date=appt_date,
        start_time=start_t,
        end_time=end_t,
        status=AppointmentStatus.BOOKED,
        notes=data.get("notes")
    )

    try:
        db.session.add(appointment)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise APIError("Double-booking prevented: Slot was taken concurrently", 409)

    return jsonify({"message": "Appointment booked successfully", "appointment_id": appointment.id}), 201

@appointments_bp.route("/my", methods=["GET"])
def get_my_appointments():
    current_user = get_current_user_from_header()

    if current_user.role == UserRole.DOCTOR:
        profile = DoctorProfile.query.filter_by(user_id=current_user.id).first_or_404()
        appts = Appointment.query.filter_by(doctor_id=profile.id).order_by(Appointment.appointment_date.asc()).all()
    else:
        appts = Appointment.query.filter_by(patient_id=current_user.id).order_by(Appointment.appointment_date.asc()).all()

    results = [{
        "id": a.id,
        "doctor_id": a.doctor_id,
        "patient_id": a.patient_id,
        "date": a.appointment_date.strftime("%Y-%m-%d"),
        "start_time": a.start_time.strftime("%H:%M"),
        "end_time": a.end_time.strftime("%H:%M"),
        "status": a.status.value
    } for a in appts]

    return jsonify({"appointments": results}), 200

@appointments_bp.route("/<int:appointment_id>/cancel", methods=["PATCH"])
def cancel_appointment(appointment_id):
    current_user = get_current_user_from_header()

    appt = Appointment.query.get_or_404(appointment_id)

    # Authorization Check: Patient can only cancel their OWN appointment
    if current_user.role == UserRole.PATIENT and appt.patient_id != current_user.id:
        raise APIError("Unauthorized: You cannot cancel another patient's appointment", 403)

    if appt.status == AppointmentStatus.CANCELLED:
        raise APIError("Appointment is already cancelled", 400)

    appt.status = AppointmentStatus.CANCELLED
    db.session.commit()

    return jsonify({"message": "Appointment cancelled successfully"}), 200