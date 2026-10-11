from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import timedelta

import database
import models
import schemas
import crud
import auth

# Create tables (including users table)
models.Base.metadata.create_all(bind=database.engine)

# Initialize FastAPI App
app = FastAPI(
    title="Healthcare Patient Management System API",
    description="RESTful API microservice with Role-Based Access Control.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS Middleware
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# HEALTH CHECK
# ==========================================
@app.get("/", tags=["Health Check"])
def root_health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "Healthcare Patient Management API v2",
        "swagger_docs": "http://127.0.0.1:8000/docs"
    }


# ==========================================
# AUTH ENDPOINTS
# ==========================================
@app.post("/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register(user_in: schemas.UserRegister, db: Session = Depends(database.get_db)):
    """Register a new user. Role must be: administrator | clinical_operations | analyst."""
    if user_in.role not in auth.VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Role must be one of: {', '.join(auth.VALID_ROLES)}")
    existing = db.query(models.User).filter(
        (models.User.username == user_in.username) | (models.User.email == user_in.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered.")
    user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=auth.hash_password(user_in.password),
        role=user_in.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=schemas.Token, tags=["Auth"])
def login(form_data: schemas.UserLogin, db: Session = Depends(database.get_db)):
    """Login with username + password. Returns a JWT access token."""
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is disabled.")
    token = auth.create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer", "role": user.role, "username": user.username}


@app.get("/auth/me", response_model=schemas.UserResponse, tags=["Auth"])
def me(current_user: models.User = Depends(auth.get_current_user)):
    """Return info about the currently authenticated user."""
    return current_user


@app.get("/auth/users", response_model=List[schemas.UserResponse], tags=["Auth"])
def list_users(
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.require_administrator),
):
    """Administrator only: list all registered users."""
    return db.query(models.User).all()


@app.patch("/auth/users/{user_id}/role", response_model=schemas.UserResponse, tags=["Auth"])
def update_user_role(
    user_id: int,
    role: str = Query(..., description="New role: administrator | clinical_operations | analyst"),
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.require_administrator),
):
    """Administrator only: change the role of any user."""
    if role not in auth.VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Role must be one of: {', '.join(auth.VALID_ROLES)}")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.role = role
    db.commit()
    db.refresh(user)
    return user


# ==========================================
# PATIENT ENDPOINTS
# ==========================================
@app.get("/api/patients", response_model=schemas.PaginatedPatients, tags=["Patients"])
def list_patients(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.require_patient_access),   # administrator | clinical_operations only
):
    """Retrieve paginated patient records. Analyst role cannot access this."""
    return crud.get_patients(db=db, page=page, limit=limit, search=search)


@app.post("/api/patients", response_model=schemas.PatientResponse, status_code=status.HTTP_201_CREATED, tags=["Patients"])
def create_patient(
    patient: schemas.PatientCreate,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.require_clinical_ops),     # administrator | clinical_operations
):
    """Create a new patient record. Requires administrator or clinical_operations role."""
    existing = crud.get_patient(db=db, patient_nbr=patient.patient_nbr)
    if existing:
        raise HTTPException(status_code=400, detail=f"Patient '{patient.patient_nbr}' already exists.")
    return crud.create_patient(db=db, patient=patient)


@app.get("/api/patients/{patient_nbr}", response_model=schemas.PatientResponse, tags=["Patients"])
def get_patient(
    patient_nbr: str,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.require_patient_access),
):
    """Retrieve a specific patient. Analyst role cannot access this."""
    patient = crud.get_patient(db=db, patient_nbr=patient_nbr)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_nbr}' not found.")
    return patient


@app.put("/api/patients/{patient_nbr}", response_model=schemas.PatientResponse, tags=["Patients"])
def update_patient(
    patient_nbr: str,
    patient_update: schemas.PatientUpdate,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.require_clinical_ops),
):
    """Update patient demographics. Requires administrator or clinical_operations role."""
    updated = crud.update_patient(db=db, patient_nbr=patient_nbr, patient_update=patient_update)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_nbr}' not found.")
    return updated


@app.delete("/api/patients/{patient_nbr}", status_code=status.HTTP_204_NO_CONTENT, tags=["Patients"])
def delete_patient(
    patient_nbr: str,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.require_administrator),    # administrator only
):
    """Delete a patient record. Requires administrator role."""
    success = crud.delete_patient(db=db, patient_nbr=patient_nbr)
    if not success:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_nbr}' not found.")
    return None


# ==========================================
# ENCOUNTER ENDPOINTS
# ==========================================
@app.get("/api/encounters", response_model=schemas.PaginatedEncounters, tags=["Encounters"])
def list_encounters(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    readmitted: Optional[str] = Query(None),
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.require_patient_access),   # administrator | clinical_operations only
):
    """Retrieve paginated encounters. Analyst role cannot access this."""
    return crud.get_encounters(db=db, page=page, limit=limit, search=search, readmitted=readmitted)


@app.post("/api/encounters", response_model=schemas.EncounterResponse, status_code=status.HTTP_201_CREATED, tags=["Encounters"])
def create_encounter(
    encounter: schemas.EncounterCreate,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.require_clinical_ops),
):
    """Create a new encounter. Requires administrator or clinical_operations role."""
    existing = crud.get_encounter(db=db, encounter_id=encounter.encounter_id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Encounter '{encounter.encounter_id}' already exists.")
    return crud.create_encounter(db=db, encounter=encounter)


@app.get("/api/encounters/{encounter_id}", response_model=schemas.EncounterResponse, tags=["Encounters"])
def get_encounter(
    encounter_id: int,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.require_patient_access),
):
    """Retrieve a specific encounter. Analyst role cannot access this."""
    encounter = crud.get_encounter(db=db, encounter_id=encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail=f"Encounter '{encounter_id}' not found.")
    return encounter


@app.put("/api/encounters/{encounter_id}", response_model=schemas.EncounterResponse, tags=["Encounters"])
def update_encounter(
    encounter_id: int,
    encounter_update: schemas.EncounterUpdate,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.require_clinical_ops),
):
    """Update an encounter. Requires administrator or clinical_operations role."""
    updated = crud.update_encounter(db=db, encounter_id=encounter_id, encounter_update=encounter_update)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Encounter '{encounter_id}' not found.")
    return updated


@app.delete("/api/encounters/{encounter_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Encounters"])
def delete_encounter(
    encounter_id: int,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.require_administrator),
):
    """Delete an encounter. Requires administrator role."""
    success = crud.delete_encounter(db=db, encounter_id=encounter_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Encounter '{encounter_id}' not found.")
    return None


# ==========================================
# ANALYTICS ENDPOINTS  (all 3 roles can access)
# ==========================================
@app.get("/api/analytics/summary", response_model=schemas.AnalyticsSummary, tags=["Analytics"])
def get_summary(
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.require_any),
):
    return crud.get_analytics_summary(db)


@app.get("/api/analytics/readmissions", tags=["Analytics"])
def get_readmission_analytics(
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.require_any),
):
    return crud.get_readmission_stats(db)


@app.get("/api/analytics/length-of-stay", tags=["Analytics"])
def get_stay_analytics(
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.require_any),
):
    return crud.get_length_of_stay_distribution(db)


@app.get("/api/analytics/demographics", tags=["Analytics"])
def get_demographics_analytics(
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.require_any),
):
    return crud.get_demographics_distribution(db)
