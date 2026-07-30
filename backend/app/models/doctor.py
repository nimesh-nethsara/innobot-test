# from app.extensions import db

# class DoctorProfile(db.Model):
#     __tablename__ = "doctor_profiles"

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
#     specialty = db.Column(db.String(100), nullable=False, index=True)
#     bio = db.Column(db.Text, nullable=True)
#     consultation_fee = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)

#     availabilities = db.relationship("DoctorAvailability", backref="doctor", cascade="all, delete-orphan")
#     appointments = db.relationship("Appointment", backref="doctor", lazy="dynamic")

# class DoctorAvailability(db.Model):
#     __tablename__ = "doctor_availabilities"

#     id = db.Column(db.Integer, primary_key=True)
#     doctor_id = db.Column(db.Integer, db.ForeignKey("doctor_profiles.id"), nullable=False)
#     day_of_week = db.Column(db.SmallInteger, nullable=False)  # 0=Mon, 6=Sun
#     start_time = db.Column(db.Time, nullable=False)
#     end_time = db.Column(db.Time, nullable=False)
#     slot_duration_mins = db.Column(db.Integer, nullable=False, default=30)

from app.extensions import db

class DoctorProfile(db.Model):
    __tablename__ = "doctor_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    specialty = db.Column(db.String(100), nullable=False, index=True)
    bio = db.Column(db.Text, nullable=True)
    consultation_fee = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)

    availabilities = db.relationship("DoctorAvailability", backref="doctor", cascade="all, delete-orphan")
    appointments = db.relationship("Appointment", backref="doctor", lazy="dynamic")

class DoctorAvailability(db.Model):
    __tablename__ = "doctor_availabilities"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor_profiles.id"), nullable=False)
    day_of_week = db.Column(db.SmallInteger, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    slot_duration_mins = db.Column(db.Integer, nullable=False, default=30)