# Healthcare Dataset Specification & Preprocessing Report

## 1. Dataset Overview
* **Dataset Name**: Diabetes 130-US Hospitals for Years 1999-2008
* **Source**: UCI Machine Learning Repository (Dataset #296)
* **Raw Files Present in Workspace**:
  * `data/raw/diabetic_data.csv` (101,766 records, 50 attributes)
  * `data/raw/IDS_mapping.csv` (Lookup mappings for admission types, discharge dispositions, and admission sources)
* **Target Analytical Domain**: Hospital encounters, inpatient length of stay, medication changes, and 30-day hospital readmission rates.

---

## 2. Key Dataset Fields

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `encounter_id` | Integer | Unique identifier for each hospital encounter (Primary Key) |
| `patient_nbr` | String | Unique identifier for each patient (Foreign Key in encounters) |
| `race` | String | Demographic race/ethnicity (Caucasian, AfricanAmerican, Hispanic, Asian, Other) |
| `gender` | String | Gender of patient (Female, Male, Unknown) |
| `age` | String | Age bracket in 10-year intervals, e.g., `[60-70)` |
| `weight` | String | Weight range (contains missing entries `'?'`) |
| `admission_type_id` | Integer | ID corresponding to admission type (Emergency, Urgent, Elective, etc.) |
| `discharge_disposition_id` | Integer | ID corresponding to discharge destination (Home, SNF, ICF, etc.) |
| `admission_source_id` | Integer | ID corresponding to referral source |
| `time_in_hospital` | Integer | Length of stay in days (integer 1 to 14) |
| `payer_code` | String | Insurance payer code |
| `medical_specialty` | String | Specialty of admitting physician |
| `num_lab_procedures` | Integer | Number of lab tests performed during encounter |
| `num_procedures` | Integer | Number of non-lab medical/surgical procedures performed |
| `num_medications` | Integer | Number of distinct medications administered |
| `number_outpatient` | Integer | Outpatient visits in year prior to encounter |
| `number_emergency` | Integer | Emergency room visits in year prior to encounter |
| `number_inpatient` | Integer | Inpatient admissions in year prior to encounter |
| `diag_1`, `diag_2`, `diag_3` | String | Primary, secondary, and tertiary ICD-9 diagnosis codes |
| `number_diagnoses` | Integer | Total number of diagnoses entered into medical system |
| `max_glu_serum`, `A1Cresult` | String | Glucose serum and HbA1c test results (`None`, `Norm`, `>7`, `>8`) |
| `insulin`, `metformin`, etc. | String | Dosage change indicators (`No`, `Steady`, `Up`, `Down`) |
| `med_change` | String | Indicator if diabetes medication was changed (`Ch` or `No`) |
| `diabetesMed` | String | Indicator if any diabetes medication was prescribed (`Yes` or `No`) |
| `readmitted` | String | Target outcome: `<30` (readmitted within 30 days), `>30` (after 30 days), `NO` |

---

## 3. Data Cleaning & Transformation Pipeline

1. **Standardization of Missing Values**:
   - Replaced raw character `'?'` entries with Python `None` / Pandas `NaN`.
   - Missing fields identified: `weight` (96.8%), `payer_code` (39.6%), `medical_specialty` (49.1%), `race` (2.2%), `diag_1` (0.02%), `diag_2` (0.35%), `diag_3` (1.4%).
2. **Deduplication**:
   - Verified 101,766 unique encounter records by `encounter_id`.
3. **Patient Entity Extraction**:
   - Grouped dataset by `patient_nbr` to isolate 71,518 unique patients.
   - Retained most recent demographic profile per patient.
4. **Keyword Collision Resolution**:
   - Renamed reserved SQL keyword column `change` to `med_change`.
   - Renamed hyphenated medication columns (`glyburide-metformin` → `glyburide_metformin`) to valid SQL identifiers.
5. **Output Generation**:
   - Cleaned datasets saved to `data/cleaned/cleaned_patients.csv`, `cleaned_encounters.csv`, and `cleaned_id_mappings.csv`.
