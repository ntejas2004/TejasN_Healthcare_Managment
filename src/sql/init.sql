-- MySQL Schema Initialization Script for Healthcare Patient Management System

CREATE DATABASE IF NOT EXISTS healthcare_db;
USE healthcare_db;

-- Table 1: Patients
CREATE TABLE IF NOT EXISTS patients (
    patient_nbr VARCHAR(50) PRIMARY KEY,
    race VARCHAR(50),
    gender VARCHAR(20),
    age VARCHAR(20),
    weight VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_patient_nbr (patient_nbr)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 2: ID Mappings
CREATE TABLE IF NOT EXISTS id_mappings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    mapping_id INT NOT NULL,
    description VARCHAR(255),
    INDEX idx_category_mapping (category, mapping_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 3: Encounters
CREATE TABLE IF NOT EXISTS encounters (
    encounter_id INT PRIMARY KEY,
    patient_nbr VARCHAR(50) NOT NULL,
    admission_type_id INT,
    discharge_disposition_id INT,
    admission_source_id INT,
    time_in_hospital INT,
    payer_code VARCHAR(50),
    medical_specialty VARCHAR(100),
    num_lab_procedures INT,
    num_procedures INT,
    num_medications INT,
    number_outpatient INT,
    number_emergency INT,
    number_inpatient INT,
    diag_1 VARCHAR(50),
    diag_2 VARCHAR(50),
    diag_3 VARCHAR(50),
    number_diagnoses INT,
    max_glu_serum VARCHAR(20),
    A1Cresult VARCHAR(20),
    metformin VARCHAR(20),
    repaglinide VARCHAR(20),
    nateglinide VARCHAR(20),
    chlorpropamide VARCHAR(20),
    glimepiride VARCHAR(20),
    acetohexamide VARCHAR(20),
    glipizide VARCHAR(20),
    glyburide VARCHAR(20),
    tolbutamide VARCHAR(20),
    pioglitazone VARCHAR(20),
    rosiglitazone VARCHAR(20),
    acarbose VARCHAR(20),
    miglitol VARCHAR(20),
    troglitazone VARCHAR(20),
    tolazamide VARCHAR(20),
    examide VARCHAR(20),
    citoglipton VARCHAR(20),
    insulin VARCHAR(20),
    glyburide_metformin VARCHAR(20),
    glipizide_metformin VARCHAR(20),
    glimepiride_pioglitazone VARCHAR(20),
    metformin_rosiglitazone VARCHAR(20),
    metformin_pioglitazone VARCHAR(20),
    med_change VARCHAR(20),
    diabetesMed VARCHAR(20),
    readmitted VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_encounters_patient FOREIGN KEY (patient_nbr) REFERENCES patients(patient_nbr) ON DELETE CASCADE,
    INDEX idx_encounter_patient (patient_nbr),
    INDEX idx_readmitted (readmitted),
    INDEX idx_time_in_hospital (time_in_hospital)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
