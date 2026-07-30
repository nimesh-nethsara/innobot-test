import pytest
from datetime import date, datetime, timedelta
from app import create_app, db
from app.config import TestingConfig
from app.models.user import User, UserRole
from app.models.doctor import DoctorProfile
from app.models.appointment import Appointment, AppointmentStatus

@pytest.fixture
def client():
    app = create_app(TestingConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_prevent_double_booking_and_past_slots(client):
    patient1 = User(full_name="Patient One", email="p1@test.com", role=UserRole.PATIENT)
    patient2 = User(full_name="Patient Two", email="p2@test.com", role=UserRole.PATIENT)
    doc_user = User(full_name="Dr. Smith", email="doc@test.com", role=UserRole.DOCTOR)
    
    db.session.add_all([patient1, patient2, doc_user])
    db.session.commit()

    profile = DoctorProfile(user_id=doc_user.id, specialty="Cardiology")
    db.session.add(profile)
    db.session.commit()

    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    payload = {
        "doctor_id": profile.id,
        "appointment_date": tomorrow,
        "start_time": "10:00",
        "end_time": "10:30"
    }

    # 1. Book initial slot with Patient 1 (X-User-Id: patient1.id)
    booking_res = client.post("/api/appointments", json=payload, headers={"X-User-Id": str(patient1.id)})
    assert booking_res.status_code == 201

    # 2. Double booking test with Patient 2 -> 409 Conflict
    double_res = client.post("/api/appointments", json=payload, headers={"X-User-Id": str(patient2.id)})
    assert double_res.status_code == 409
    assert "already booked" in double_res.json["error"]

    # 3. Past date booking attempt -> 400 Bad Request
    past_payload = {
        "doctor_id": profile.id,
        "appointment_date": "2020-01-01",
        "start_time": "10:00",
        "end_time": "10:30"
    }
    past_res = client.post("/api/appointments", json=past_payload, headers={"X-User-Id": str(patient1.id)})
    assert past_res.status_code == 400
    assert "Cannot book an appointment in the past" in past_res.json["error"]

def test_prevent_unauthorized_cancellation(client):
    patient1 = User(full_name="P1", email="p1@test.com", role=UserRole.PATIENT)
    patient2 = User(full_name="P2", email="p2@test.com", role=UserRole.PATIENT)
    doc_user = User(full_name="Dr. Smith", email="doc@test.com", role=UserRole.DOCTOR)
    
    db.session.add_all([patient1, patient2, doc_user])
    db.session.commit()
    profile = DoctorProfile(user_id=doc_user.id, specialty="Cardiology")
    db.session.add(profile)
    db.session.commit()

    appt = Appointment(
        patient_id=patient1.id,
        doctor_id=profile.id,
        appointment_date=date.today() + timedelta(days=1),
        start_time=datetime.strptime("11:00", "%H:%M").time(),
        end_time=datetime.strptime("11:30", "%H:%M").time(),
        status=AppointmentStatus.BOOKED
    )
    db.session.add(appt)
    db.session.commit()

    # Patient 2 attempts to cancel Patient 1's appointment -> 403 Forbidden
    cancel_res = client.patch(f"/api/appointments/{appt.id}/cancel", headers={"X-User-Id": str(patient2.id)})
    assert cancel_res.status_code == 403
    assert "Unauthorized" in cancel_res.json["error"]