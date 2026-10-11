from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """SQLAlchemy model for system users with role-based access control."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="viewer")  # admin | doctor | viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class Patient(Base):
    """SQLAlchemy model representing a unique patient in the healthcare system."""
    __tablename__ = "patients"

    patient_nbr = Column(String(50), primary_key=True, index=True)
    race = Column(String(50), nullable=True)
    gender = Column(String(20), nullable=True)
    age = Column(String(20), nullable=True)
    weight = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship to encounters
    encounters = relationship(
        "Encounter",
        back_populates="patient",
        cascade="all, delete-orphan"
    )


class IDMapping(Base):
    """SQLAlchemy model for lookup descriptions (admission type, discharge disposition, etc.)."""
    __tablename__ = "id_mappings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False)
    mapping_id = Column(Integer, nullable=False)
    description = Column(String(255), nullable=True)


class Encounter(Base):
    """SQLAlchemy model representing a single hospital visit/encounter."""
    __tablename__ = "encounters"

    encounter_id = Column(Integer, primary_key=True)
    patient_nbr = Column(String(50), ForeignKey("patients.patient_nbr"), nullable=False, index=True)
    
    admission_type_id = Column(Integer, nullable=True)
    discharge_disposition_id = Column(Integer, nullable=True)
    admission_source_id = Column(Integer, nullable=True)
    time_in_hospital = Column(Integer, nullable=True)
    payer_code = Column(String(50), nullable=True)
    medical_specialty = Column(String(100), nullable=True)
    
    num_lab_procedures = Column(Integer, nullable=True)
    num_procedures = Column(Integer, nullable=True)
    num_medications = Column(Integer, nullable=True)
    number_outpatient = Column(Integer, nullable=True)
    number_emergency = Column(Integer, nullable=True)
    number_inpatient = Column(Integer, nullable=True)
    
    diag_1 = Column(String(50), nullable=True)
    diag_2 = Column(String(50), nullable=True)
    diag_3 = Column(String(50), nullable=True)
    number_diagnoses = Column(Integer, nullable=True)
    
    max_glu_serum = Column(String(20), nullable=True)
    A1Cresult = Column(String(20), nullable=True)
    metformin = Column(String(20), nullable=True)
    repaglinide = Column(String(20), nullable=True)
    nateglinide = Column(String(20), nullable=True)
    chlorpropamide = Column(String(20), nullable=True)
    glimepiride = Column(String(20), nullable=True)
    acetohexamide = Column(String(20), nullable=True)
    glipizide = Column(String(20), nullable=True)
    glyburide = Column(String(20), nullable=True)
    tolbutamide = Column(String(20), nullable=True)
    pioglitazone = Column(String(20), nullable=True)
    rosiglitazone = Column(String(20), nullable=True)
    acarbose = Column(String(20), nullable=True)
    miglitol = Column(String(20), nullable=True)
    troglitazone = Column(String(20), nullable=True)
    tolazamide = Column(String(20), nullable=True)
    examide = Column(String(20), nullable=True)
    citoglipton = Column(String(20), nullable=True)
    insulin = Column(String(20), nullable=True)
    glyburide_metformin = Column(String(20), nullable=True)
    glipizide_metformin = Column(String(20), nullable=True)
    glimepiride_pioglitazone = Column(String(20), nullable=True)
    metformin_rosiglitazone = Column(String(20), nullable=True)
    metformin_pioglitazone = Column(String(20), nullable=True)
    
    med_change = Column(String(20), nullable=True)
    diabetesMed = Column(String(20), nullable=True)
    readmitted = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship back to patient
    patient = relationship("Patient", back_populates="encounters")
