# import enum
# from app.extensions import db

# class AppointmentStatus(str, enum.Enum):
#     BOOKED = "BOOKED"
#     CANCELLED = "CANCELLED"
#     COMPLETED = "COMPLETED"

# class Appointment(db.Model):
#     __tablename__ = "appointments"

#     id = db.Column(db.Integer, primary_key=True)
#     patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
#     doctor_id = db.Column(db.Integer, db.ForeignKey("doctor_profiles.id"), nullable=False)
#     appointment_date = db.Column(db.Date, nullable=False, index=True)
#     start_time = db.Column(db.Time, nullable=False)
#     end_time = db.Column(db.Time, nullable=False)
#     status = db.Column(db.Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.BOOKED)
#     notes = db.Column(db.Text, nullable=True)
#     created_at = db.Column(db.DateTime, server_default=db.func.now())

#     # Database-level Partial Unique Index to prevent double-booking at SQL level
#     __table_args__ = (
#         db.Index(
#             "idx_unique_active_doctor_slot",
#             "doctor_id", "appointment_date", "start_time",
#             unique=True,
#             postgresql_where=(status == AppointmentStatus.BOOKED),
#             sqlite_where=(status == 'BOOKED')
#         ),
#     )

import enum
from app.extensions import db

class AppointmentStatus(str, enum.Enum):
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor_profiles.id"), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.BOOKED)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Partial Unique Index to prevent double-booking at the database layer
    __table_args__ = (
        db.Index(
            "idx_unique_active_doctor_slot",
            "doctor_id", "appointment_date", "start_time",
            unique=True,
            postgresql_where=(status == AppointmentStatus.BOOKED),
            sqlite_where=(status == 'BOOKED')
        ),
    )