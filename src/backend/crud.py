import json
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
import models
import schemas


def log_audit(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: str,
    performed_by: str,
    user_role: str = None,
    details: dict = None
):
    """Persist an audit log entry documenting data changes and user provenance."""
    details_str = json.dumps(details) if isinstance(details, dict) else (str(details) if details else None)
    log_entry = models.AuditLog(
        action=action.upper(),
        entity_type=entity_type,
        entity_id=str(entity_id),
        performed_by=performed_by,
        user_role=user_role,
        details=details_str
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


def get_audit_logs(
    db: Session,
    page: int = 1,
    limit: int = 25,
    action: str = None,
    entity_type: str = None,
    search: str = None
):
    """Retrieve paginated audit logs with optional filters."""
    query = db.query(models.AuditLog)
    if action and action != "ALL":
        query = query.filter(models.AuditLog.action == action.upper())
    if entity_type and entity_type != "ALL":
        query = query.filter(models.AuditLog.entity_type == entity_type)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                models.AuditLog.entity_id.like(search_fmt),
                models.AuditLog.performed_by.like(search_fmt),
                models.AuditLog.details.like(search_fmt)
            )
        )
    total = query.count()
    offset = (page - 1) * limit
    data = query.order_by(models.AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
    return {"total": total, "page": page, "limit": limit, "data": data}


# ------------------------------
# Patient CRUD Operations
# ------------------------------
def get_patient(db: Session, patient_nbr: str):
    """Retrieve a patient by unique patient_nbr."""
    return db.query(models.Patient).filter(models.Patient.patient_nbr == patient_nbr).first()


def get_patients(db: Session, page: int = 1, limit: int = 20, search: str = None):
    """Retrieve paginated patients with optional search by patient_nbr, race, or gender."""
    query = db.query(models.Patient)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                models.Patient.patient_nbr.like(search_fmt),
                models.Patient.race.like(search_fmt),
                models.Patient.gender.like(search_fmt)
            )
        )
    total = query.count()
    offset = (page - 1) * limit
    data = query.offset(offset).limit(limit).all()
    return {"total": total, "page": page, "limit": limit, "data": data}


def create_patient(db: Session, patient: schemas.PatientCreate):
    """Create a new patient record."""
    db_patient = models.Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def update_patient(db: Session, patient_nbr: str, patient_update: schemas.PatientUpdate):
    """Update an existing patient record."""
    db_patient = get_patient(db, patient_nbr)
    if not db_patient:
        return None
    update_data = patient_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_patient, key, value)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def delete_patient(db: Session, patient_nbr: str):
    """Delete a patient record and cascaded encounters."""
    db_patient = get_patient(db, patient_nbr)
    if not db_patient:
        return False
    db.delete(db_patient)
    db.commit()
    return True


# ------------------------------
# Encounter CRUD Operations
# ------------------------------
def get_encounter(db: Session, encounter_id: int):
    """Retrieve an encounter by encounter_id."""
    return db.query(models.Encounter).filter(models.Encounter.encounter_id == encounter_id).first()


def get_encounters(db: Session, page: int = 1, limit: int = 20, search: str = None, readmitted: str = None):
    """Retrieve paginated encounters with optional search and filtering."""
    query = db.query(models.Encounter)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                models.Encounter.patient_nbr.like(search_fmt),
                models.Encounter.medical_specialty.like(search_fmt),
                models.Encounter.diag_1.like(search_fmt)
            )
        )
    if readmitted and readmitted != "ALL":
        query = query.filter(models.Encounter.readmitted == readmitted)
    total = query.count()
    offset = (page - 1) * limit
    data = query.order_by(models.Encounter.encounter_id.desc()).offset(offset).limit(limit).all()
    return {"total": total, "page": page, "limit": limit, "data": data}


def create_encounter(db: Session, encounter: schemas.EncounterCreate):
    """Create a new encounter record. Ensures patient exists first."""
    # Ensure patient exists
    db_patient = get_patient(db, encounter.patient_nbr)
    if not db_patient:
        db_patient = models.Patient(patient_nbr=encounter.patient_nbr, race="Unknown", gender="Unknown", age="Unknown")
        db.add(db_patient)
        db.commit()

    db_encounter = models.Encounter(**encounter.model_dump())
    db.add(db_encounter)
    db.commit()
    db.refresh(db_encounter)
    return db_encounter


def update_encounter(db: Session, encounter_id: int, encounter_update: schemas.EncounterUpdate):
    """Update an existing encounter record."""
    db_encounter = get_encounter(db, encounter_id)
    if not db_encounter:
        return None
    update_data = encounter_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_encounter, key, value)
    db.commit()
    db.refresh(db_encounter)
    return db_encounter


def delete_encounter(db: Session, encounter_id: int):
    """Delete an encounter record."""
    db_encounter = get_encounter(db, encounter_id)
    if not db_encounter:
        return False
    db.delete(db_encounter)
    db.commit()
    return True


# ------------------------------
# Healthcare Operational Analytics
# ------------------------------
def get_analytics_summary(db: Session):
    """Compute overall operational metrics across patients and encounters."""
    total_patients = db.query(models.Patient).count()
    total_encounters = db.query(models.Encounter).count()

    readmitted_count = db.query(models.Encounter).filter(
        models.Encounter.readmitted.in_(["<30", ">30"])
    ).count()

    readmission_rate = round((readmitted_count / total_encounters * 100), 2) if total_encounters > 0 else 0.0

    avg_stay = db.query(func.avg(models.Encounter.time_in_hospital)).scalar() or 0.0
    avg_meds = db.query(func.avg(models.Encounter.num_medications)).scalar() or 0.0
    avg_labs = db.query(func.avg(models.Encounter.num_lab_procedures)).scalar() or 0.0

    return {
        "total_patients": total_patients,
        "total_encounters": total_encounters,
        "readmission_rate_pct": readmission_rate,
        "avg_length_of_stay_days": round(float(avg_stay), 2),
        "avg_num_medications": round(float(avg_meds), 2),
        "avg_lab_procedures": round(float(avg_labs), 2)
    }


def get_readmission_stats(db: Session):
    """Compute breakdown of readmission categories (<30, >30, NO)."""
    total = db.query(models.Encounter).count()
    results = db.query(
        models.Encounter.readmitted,
        func.count(models.Encounter.encounter_id)
    ).group_by(models.Encounter.readmitted).all()

    items = []
    for cat, count in results:
        category_label = cat if cat else "Unspecified"
        pct = round((count / total * 100), 2) if total > 0 else 0.0
        items.append({
            "category": category_label,
            "count": count,
            "percentage": pct
        })
    return items


def get_length_of_stay_distribution(db: Session):
    """Compute encounter counts grouped by length of stay in days."""
    results = db.query(
        models.Encounter.time_in_hospital,
        func.count(models.Encounter.encounter_id)
    ).group_by(models.Encounter.time_in_hospital).order_by(models.Encounter.time_in_hospital).all()

    return [{"days": int(days or 0), "count": count} for days, count in results]


def get_demographics_distribution(db: Session):
    """Compute breakdown of patients by race and gender."""
    race_results = db.query(
        models.Patient.race,
        func.count(models.Patient.patient_nbr)
    ).group_by(models.Patient.race).all()

    gender_results = db.query(
        models.Patient.gender,
        func.count(models.Patient.patient_nbr)
    ).group_by(models.Patient.gender).all()

    return {
        "race": [{"category": r[0] or "Unknown", "count": r[1]} for r in race_results],
        "gender": [{"category": g[0] or "Unknown", "count": g[1]} for g in gender_results]
    }
