import enum
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class UserRole(str, enum.Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.PATIENT)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    doctor_profile = db.relationship("DoctorProfile", backref="user", uselist=False, cascade="all, delete-orphan")
    appointments = db.relationship("Appointment", backref="patient", lazy="dynamic")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)