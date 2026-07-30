from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User, UserRole
from app.models.doctor import DoctorProfile
from app.utils.errors import APIError

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    role = data.get("role", "PATIENT").upper()

    if not email or not password or not full_name:
        raise APIError("Missing required fields: email, password, full_name", 400)

    if User.query.filter_by(email=email).first():
        raise APIError("Email already registered", 409)

    user = User(
        full_name=full_name,
        email=email,
        role=UserRole(role) if role in UserRole.__members__ else UserRole.PATIENT
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    if user.role == UserRole.DOCTOR:
        specialty = data.get("specialty", "General Practitioner")
        profile = DoctorProfile(user_id=user.id, specialty=specialty)
        db.session.add(profile)

    db.session.commit()
    return jsonify({"message": "User registered successfully", "id": user.id}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise APIError("Invalid email or password", 401)

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id, 
            "email": user.email, 
            "role": user.role.value,
            "full_name": user.full_name
        }
    }), 200