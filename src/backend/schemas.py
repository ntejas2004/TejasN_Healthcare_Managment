try:
    from pydantic import EmailStr
except ImportError:
    EmailStr = str

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# ------------------------------
# Auth / User Schemas
# ------------------------------
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    email: str = Field(..., max_length=120)
    password: str = Field(..., min_length=6)
    role: Optional[str] = Field("analyst", description="administrator | clinical_operations | analyst")


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True



# ------------------------------
# Patient Schemas
# ------------------------------
class PatientBase(BaseModel):
    patient_nbr: str = Field(..., description="Unique patient identifier")
    race: Optional[str] = Field(None, description="Patient race/ethnicity")
    gender: Optional[str] = Field(None, description="Patient gender")
    age: Optional[str] = Field(None, description="Patient age bracket, e.g., [70-80)")
    weight: Optional[str] = Field(None, description="Patient weight range")


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    race: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[str] = None
    weight: Optional[str] = None


class PatientResponse(PatientBase):
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaginatedPatients(BaseModel):
    total: int
    page: int
    limit: int
    data: List[PatientResponse]


# ------------------------------
# Encounter Schemas
# ------------------------------
class EncounterBase(BaseModel):
    encounter_id: int
    patient_nbr: str
    admission_type_id: Optional[int] = 1
    discharge_disposition_id: Optional[int] = 1
    admission_source_id: Optional[int] = 1
    time_in_hospital: Optional[int] = 1
    payer_code: Optional[str] = None
    medical_specialty: Optional[str] = None
    num_lab_procedures: Optional[int] = 0
    num_procedures: Optional[int] = 0
    num_medications: Optional[int] = 0
    number_outpatient: Optional[int] = 0
    number_emergency: Optional[int] = 0
    number_inpatient: Optional[int] = 0
    diag_1: Optional[str] = None
    diag_2: Optional[str] = None
    diag_3: Optional[str] = None
    number_diagnoses: Optional[int] = 1
    max_glu_serum: Optional[str] = "None"
    A1Cresult: Optional[str] = "None"
    metformin: Optional[str] = "No"
    repaglinide: Optional[str] = "No"
    nateglinide: Optional[str] = "No"
    chlorpropamide: Optional[str] = "No"
    glimepiride: Optional[str] = "No"
    acetohexamide: Optional[str] = "No"
    glipizide: Optional[str] = "No"
    glyburide: Optional[str] = "No"
    tolbutamide: Optional[str] = "No"
    pioglitazone: Optional[str] = "No"
    rosiglitazone: Optional[str] = "No"
    acarbose: Optional[str] = "No"
    miglitol: Optional[str] = "No"
    troglitazone: Optional[str] = "No"
    tolazamide: Optional[str] = "No"
    examide: Optional[str] = "No"
    citoglipton: Optional[str] = "No"
    insulin: Optional[str] = "No"
    glyburide_metformin: Optional[str] = "No"
    glipizide_metformin: Optional[str] = "No"
    glimepiride_pioglitazone: Optional[str] = "No"
    metformin_rosiglitazone: Optional[str] = "No"
    metformin_pioglitazone: Optional[str] = "No"
    med_change: Optional[str] = "No"
    diabetesMed: Optional[str] = "No"
    readmitted: Optional[str] = "NO"


class EncounterCreate(EncounterBase):
    pass


class EncounterUpdate(BaseModel):
    admission_type_id: Optional[int] = None
    discharge_disposition_id: Optional[int] = None
    admission_source_id: Optional[int] = None
    time_in_hospital: Optional[int] = None
    payer_code: Optional[str] = None
    medical_specialty: Optional[str] = None
    num_lab_procedures: Optional[int] = None
    num_procedures: Optional[int] = None
    num_medications: Optional[int] = None
    diag_1: Optional[str] = None
    diag_2: Optional[str] = None
    diag_3: Optional[str] = None
    readmitted: Optional[str] = None


class EncounterResponse(EncounterBase):
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaginatedEncounters(BaseModel):
    total: int
    page: int
    limit: int
    data: List[EncounterResponse]


# ------------------------------
# Operational Analytics Schemas
# ------------------------------
class AnalyticsSummary(BaseModel):
    total_patients: int
    total_encounters: int
    readmission_rate_pct: float
    avg_length_of_stay_days: float
    avg_num_medications: float
    avg_lab_procedures: float


class ReadmissionItem(BaseModel):
    category: str
    count: int
    percentage: float


class LengthOfStayItem(BaseModel):
    days: int
    count: int


class CategoryCountItem(BaseModel):
    category: str
    count: int


# ------------------------------
# Audit Log Schemas
# ------------------------------
class AuditLogResponse(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: str
    performed_by: str
    user_role: Optional[str] = None
    details: Optional[str] = None
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaginatedAuditLogs(BaseModel):
    total: int
    page: int
    limit: int
    data: List[AuditLogResponse]
