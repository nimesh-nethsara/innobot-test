# Part 1: Patient Management System

## 1. Local Development Setup (Manual)

## backend

### Prerequisites
*   **Python 3.12+**
*   **Node.js 22+**
*   **PostgreSQL 15+** (Running locally)

### Create and activate a virtual environment:
* Windows: python -m venv venv and then venv\Scripts\activate
* Mac/Linux: python3 -m venv venv and then source venv/bin/activate

### Install the required Python packages:
* pip install -r requirements.txt

### Update your .env file in the backend directory to point to your local PostgreSQL instance:
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<db_name>
SECRET_KEY=your_secret_key

### Initialize the database tables:
* python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

### Start the Flask development server:
* python run.py

## frontend

### Open a new terminal and navigate to the frontend directory:
* cd frontend

### Install the React dependencies:
* npm install

### Ensure you have an .env file in the /frontend directory pointing to the backend:
VITE_API_BASE_URL=http://localhost:5000/api

### Start the Vite development server:
* npm run dev

## Docker Build & Production Deployment

### Option A: 1-Click Deployment (Windows)
* deploy.bat

### Option B: Manual Deployment Commands (Mac/Linux/Windows)
1) Build and start the containers in detached mode:

* docker-compose up -d --build

2) Wait a few seconds for the PostgreSQL container to fully initialize.
3) Initialize the database tables inside the running backend container:

* docker exec -it clinic_backend python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

[!NOTE]

    used design principles. created with orgaized moduler project structure. with using sqlalchemy for db managemant. and use seperate folders within app folder ,
        * models - represents database tables
        * routes - represents each endpoints and brain (all logical cases)
        * utils - includes error.py for error handling properly as best practice
        * initialize db within seperate extention.py file because avoiding circular importing
        * config.py includes all configurations with fetching keys within .env
        * within app/__init__.py include flask app creating logics and app and db bindings, app and error.py bindings

        within routes created seperate blueprints as appointment.py, auth.py, doctors.py because its best practice and moduler way for code scalable and organize logics.



# Part 2: Debugging Exercise

```python
@router.get("/doctors/{doctor_id}/schedule")
def get_schedule(doctor_id: int, date: str = ""):
query = f"""
SELECT id, patient_id, slot_time, status
FROM appointments
WHERE doctor_id = {doctor_id} AND slot_time LIKE '{date}%'
ORDER BY slot_time
"""
conn = engine.connect()
result = conn.execute(text(query))
return [dict(row) for row in result]
```
[!NOTE]

    within above code part i can see these issues

    1) check this lines -> 
    @router.get("/doctors/{doctor_id}/schedule")
    def get_schedule(doctor_id: int, date: str = ""):
        *in here date is variable for this get_schedule. it must be pass with the endpoint . but endpoint only passes doctor_id as variable.date is missing.
        
        *in this case everytime queary this part -> lot_time LIKE '{date}%' looks like lot_time LIKE '%' . it means this filtering part not working -> AND slot_time LIKE '{date}%' 

        *query completely looks like -> SELECT id, patient_id, slot_time, status FROM appointments WHERE doctor_id = {doctor_id}

        * why in demo test works -> i think from demo only one data includes within table with testing doctor_id, for that single raw every time selects perfectly. but in production selects all raws without filtering by time , but ordering datetime numarical order.

    2) slot_time and date use as string , its not good practice that datetime values save as string . and ordering with the string . i think good practice is use datetime values as datetime object with specific timezone. in flask use isoformat() as best practice

    3) and in here not validates doctor_id . if docter id='' fastapi gives automatically validation error response becaue within parameter initialized doctor_id as int -> doctor_id: int .  but doctor_id cant be 0. if doctor_id = 0 , nothing returns bot code not clean and perfect.



```python
@router.post("/appointments")
def book_appointment(patient_id: int, doctor_id: int, slot_time: str):
    conn = engine.connect()
    existing = conn.execute(
    text(f"""
        SELECT id FROM appointments
        WHERE doctor_id = {doctor_id} AND slot_time = '{slot_time}'
        AND status = 'booked'
        """)
    ).fetchone()

    if existing:
        return {"error": "Slot already booked"}
            conn.execute(
            text(f"""
            INSERT INTO appointments (patient_id, doctor_id, slot_time, status)
            VALUES ({patient_id}, {doctor_id}, '{slot_time}', 'booked')
            """)
        )

    return {"status": "booked"}

```

[!NOTE]
    4) check above code part. its post request. post request cant get data as parameters like get request . eg:book_appointment(patient_id: int, doctor_id: int, slot_time: str) this way

    with fastapi only can get data with that body passing data , add within pydantic model. in that case that pydantic model class can include as function paraeters. for above case we can write


```python
from fastapi import APIRouter
from sqlalchemy import text
from app.db import engine

router = APIRouter()

class AppointmentModel(BaseModel):
    patient_id: int
    doctor_id: int
    slot_time:str

@router.post("/appointments")
def book_appointment(data: AppointmentModel):
    conn = engine.connect()
    existing = conn.execute(
    text(f"""
        SELECT id FROM appointments
        WHERE doctor_id = {data.doctor_id} AND slot_time = '{data.slot_time}'
        AND status = 'booked'
        """)
    ).fetchone()

    if existing:
        return {"error": "Slot already booked"}
            conn.execute(
            text(f"""
            INSERT INTO appointments (patient_id, doctor_id, slot_time, status)
            VALUES ({data.patient_id}, {data.doctor_id}, '{data.slot_time}', 'booked')
            """)
        )

    return {"status": "booked"}

```

[!NOTE]

    when we changes code like above way, fastapi automatically do the data validation . if endpoint receves invalid data, fast api automatically sends the error response