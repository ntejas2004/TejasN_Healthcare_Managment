import io
import csv
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
import openpyxl

import database
import models
import schemas
import crud
import auth

# Create tables (including users & audit_logs tables)
models.Base.metadata.create_all(bind=database.engine)

# In-memory store of recent scheduled automated reports
scheduled_reports_history = []

def generate_daily_analytics_report():
    """Scheduled task: periodically aggregates and stores operational performance reports."""
    try:
        db = database.SessionLocal()
        summary = crud.get_analytics_summary(db)
        report_record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "report_name": "Scheduled Daily Clinical KPI Report",
            "total_patients": summary["total_patients"],
            "total_encounters": summary["total_encounters"],
            "readmission_rate_pct": summary["readmission_rate_pct"],
            "avg_length_of_stay_days": summary["avg_length_of_stay_days"],
            "avg_num_medications": summary["avg_num_medications"],
            "avg_lab_procedures": summary["avg_lab_procedures"],
            "status": "COMPLETED"
        }
        scheduled_reports_history.insert(0, report_record)
        # Keep latest 50 reports
        if len(scheduled_reports_history) > 50:
            scheduled_reports_history.pop()
        db.close()
    except Exception as e:
        print(f"Error executing scheduled analytics report: {e}")

# Initialize BackgroundScheduler
scheduler = BackgroundScheduler(daemon=True)
# Run immediately upon boot, then every 24 hours
scheduler.add_job(generate_daily_analytics_report, 'interval', hours=24, next_run_time=datetime.now())
scheduler.start()

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
    current_user: models.User = Depends(auth.require_clinical_ops),     # administrator | clinical_operations
):
    """Create a new patient record. Records audit log with username of creator."""
    existing = crud.get_patient(db=db, patient_nbr=patient.patient_nbr)
    if existing:
        raise HTTPException(status_code=400, detail=f"Patient '{patient.patient_nbr}' already exists.")
    created = crud.create_patient(db=db, patient=patient)
    crud.log_audit(
        db=db,
        action="CREATE",
        entity_type="Patient",
        entity_id=patient.patient_nbr,
        performed_by=current_user.username,
        user_role=current_user.role,
        details={
            "patient_nbr": patient.patient_nbr,
            "race": patient.race,
            "gender": patient.gender,
            "age": patient.age,
            "weight": patient.weight
        }
    )
    return created


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
    current_user: models.User = Depends(auth.require_clinical_ops),
):
    """Update patient demographics. Records audit log."""
    updated = crud.update_patient(db=db, patient_nbr=patient_nbr, patient_update=patient_update)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_nbr}' not found.")
    crud.log_audit(
        db=db,
        action="UPDATE",
        entity_type="Patient",
        entity_id=patient_nbr,
        performed_by=current_user.username,
        user_role=current_user.role,
        details=patient_update.model_dump(exclude_unset=True)
    )
    return updated


@app.delete("/api/patients/{patient_nbr}", status_code=status.HTTP_204_NO_CONTENT, tags=["Patients"])
def delete_patient(
    patient_nbr: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_administrator),    # administrator only
):
    """Delete a patient record. Records audit log."""
    success = crud.delete_patient(db=db, patient_nbr=patient_nbr)
    if not success:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_nbr}' not found.")
    crud.log_audit(
        db=db,
        action="DELETE",
        entity_type="Patient",
        entity_id=patient_nbr,
        performed_by=current_user.username,
        user_role=current_user.role,
        details={"status": "Patient and cascaded encounters deleted"}
    )
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
    current_user: models.User = Depends(auth.require_clinical_ops),
):
    """Create a new encounter. Records audit log with author info."""
    existing = crud.get_encounter(db=db, encounter_id=encounter.encounter_id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Encounter '{encounter.encounter_id}' already exists.")
    created = crud.create_encounter(db=db, encounter=encounter)
    crud.log_audit(
        db=db,
        action="CREATE",
        entity_type="Encounter",
        entity_id=str(encounter.encounter_id),
        performed_by=current_user.username,
        user_role=current_user.role,
        details={
            "encounter_id": encounter.encounter_id,
            "patient_nbr": encounter.patient_nbr,
            "medical_specialty": encounter.medical_specialty,
            "readmitted": encounter.readmitted
        }
    )
    return created


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
    current_user: models.User = Depends(auth.require_clinical_ops),
):
    """Update an encounter. Records audit log."""
    updated = crud.update_encounter(db=db, encounter_id=encounter_id, encounter_update=encounter_update)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Encounter '{encounter_id}' not found.")
    crud.log_audit(
        db=db,
        action="UPDATE",
        entity_type="Encounter",
        entity_id=str(encounter_id),
        performed_by=current_user.username,
        user_role=current_user.role,
        details=encounter_update.model_dump(exclude_unset=True)
    )
    return updated


@app.delete("/api/encounters/{encounter_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Encounters"])
def delete_encounter(
    encounter_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_administrator),
):
    """Delete an encounter. Records audit log."""
    success = crud.delete_encounter(db=db, encounter_id=encounter_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Encounter '{encounter_id}' not found.")
    crud.log_audit(
        db=db,
        action="DELETE",
        entity_type="Encounter",
        entity_id=str(encounter_id),
        performed_by=current_user.username,
        user_role=current_user.role,
        details={"status": "Encounter deleted"}
    )
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


# ==========================================
# AUDIT LOG ENDPOINTS
# ==========================================
@app.get("/api/audit-logs", response_model=schemas.PaginatedAuditLogs, tags=["Audit Logs"])
def list_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    action: Optional[str] = Query(None, description="CREATE | UPDATE | DELETE"),
    entity_type: Optional[str] = Query(None, description="Patient | Encounter | User"),
    search: Optional[str] = Query(None),
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.require_clinical_ops),  # administrator | clinical_operations
):
    """Retrieve paginated audit logs showing who performed what action."""
    return crud.get_audit_logs(
        db=db,
        page=page,
        limit=limit,
        action=action,
        entity_type=entity_type,
        search=search
    )


# ==========================================
# EXPORT ENDPOINTS (CSV & Excel)
# ==========================================
@app.get("/api/export/patients/csv", tags=["Export"])
def export_patients_csv(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_patient_access),
):
    """Export all patient demographics to a CSV file."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Patient Number", "Race", "Gender", "Age Bracket", "Weight Range", "Created At"])
    
    # Stream in chunks
    patients = db.query(models.Patient).limit(10000).all()
    for p in patients:
        writer.writerow([
            p.patient_nbr,
            p.race or "Unknown",
            p.gender or "Unknown",
            p.age or "Unknown",
            p.weight or "Unknown",
            p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else ""
        ])
    
    crud.log_audit(
        db=db,
        action="EXPORT",
        entity_type="Patient",
        entity_id="ALL",
        performed_by=current_user.username,
        user_role=current_user.role,
        details={"format": "CSV", "records_exported": len(patients)}
    )

    output.seek(0)
    filename = f"patients_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/api/export/patients/excel", tags=["Export"])
def export_patients_excel(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_patient_access),
):
    """Export patient demographics to an Excel spreadsheet (.xlsx)."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Patients"

    headers = ["Patient Number", "Race", "Gender", "Age Bracket", "Weight Range", "Created At"]
    ws.append(headers)

    patients = db.query(models.Patient).limit(10000).all()
    for p in patients:
        ws.append([
            p.patient_nbr,
            p.race or "Unknown",
            p.gender or "Unknown",
            p.age or "Unknown",
            p.weight or "Unknown",
            p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else ""
        ])

    crud.log_audit(
        db=db,
        action="EXPORT",
        entity_type="Patient",
        entity_id="ALL",
        performed_by=current_user.username,
        user_role=current_user.role,
        details={"format": "Excel", "records_exported": len(patients)}
    )

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    filename = f"patients_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/api/export/encounters/csv", tags=["Export"])
def export_encounters_csv(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_patient_access),
):
    """Export hospital encounters to a CSV file."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Encounter ID", "Patient Number", "Medical Specialty", "Length of Stay (Days)",
        "Lab Procedures", "Medications", "Diagnoses Count", "Readmitted"
    ])

    encounters = db.query(models.Encounter).limit(10000).all()
    for e in encounters:
        writer.writerow([
            e.encounter_id,
            e.patient_nbr,
            e.medical_specialty or "General",
            e.time_in_hospital,
            e.num_lab_procedures,
            e.num_medications,
            e.number_diagnoses,
            e.readmitted or "NO"
        ])

    crud.log_audit(
        db=db,
        action="EXPORT",
        entity_type="Encounter",
        entity_id="ALL",
        performed_by=current_user.username,
        user_role=current_user.role,
        details={"format": "CSV", "records_exported": len(encounters)}
    )

    output.seek(0)
    filename = f"encounters_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/api/export/encounters/excel", tags=["Export"])
def export_encounters_excel(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_patient_access),
):
    """Export hospital encounters to an Excel spreadsheet (.xlsx)."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Encounters"

    headers = [
        "Encounter ID", "Patient Number", "Medical Specialty", "Length of Stay (Days)",
        "Lab Procedures", "Medications", "Diagnoses Count", "Readmitted"
    ]
    ws.append(headers)

    encounters = db.query(models.Encounter).limit(10000).all()
    for e in encounters:
        ws.append([
            e.encounter_id,
            e.patient_nbr,
            e.medical_specialty or "General",
            e.time_in_hospital,
            e.num_lab_procedures,
            e.num_medications,
            e.number_diagnoses,
            e.readmitted or "NO"
        ])

    crud.log_audit(
        db=db,
        action="EXPORT",
        entity_type="Encounter",
        entity_id="ALL",
        performed_by=current_user.username,
        user_role=current_user.role,
        details={"format": "Excel", "records_exported": len(encounters)}
    )

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    filename = f"encounters_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ==========================================
# SCHEDULED REPORTING ENDPOINTS
# ==========================================
@app.get("/api/reports/scheduled", tags=["Reporting"])
def list_scheduled_reports(
    _: models.User = Depends(auth.require_any),
):
    """List historical scheduled automated operational reports generated by the background scheduler."""
    return scheduled_reports_history


@app.post("/api/reports/trigger", tags=["Reporting"])
def trigger_scheduled_report_now(
    _: models.User = Depends(auth.require_any),
):
    """On-demand trigger of the automated scheduled clinical report."""
    generate_daily_analytics_report()
    return {"message": "Scheduled report generated successfully", "latest": scheduled_reports_history[0] if scheduled_reports_history else None}
