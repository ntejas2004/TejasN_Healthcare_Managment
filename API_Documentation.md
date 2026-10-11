# Healthcare Patient Management API Specification

Interactive Swagger UI documentation is hosted live at: `http://127.0.0.1:8000/docs`.

---

## 🟢 1. System Health Check

### `GET /`
Returns system status and link to interactive OpenAPI documentation.
* **Request**: None
* **Response (200 OK)**:
```json
{
  "status": "healthy",
  "service": "Healthcare Patient Management API",
  "swagger_docs": "http://127.0.0.1:8000/docs"
}
```

---

## 👤 2. Patient Management Endpoints

### `GET /api/patients`
Retrieve paginated patient records with optional search.
* **Query Parameters**:
  * `page` (int, default=1)
  * `limit` (int, default=20)
  * `search` (string, optional) — searches `patient_nbr`, `race`, `gender`
* **Response (200 OK)**:
```json
{
  "total": 71518,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "patient_nbr": "8222157",
      "race": "Caucasian",
      "gender": "Female",
      "age": "[0-10)",
      "weight": "Unknown",
      "created_at": "2026-10-10T14:15:00"
    }
  ]
}
```

### `POST /api/patients`
Create a new patient record.
* **Request Body**:
```json
{
  "patient_nbr": "99887766",
  "race": "Caucasian",
  "gender": "Female",
  "age": "[50-60)",
  "weight": "Unknown"
}
```
* **Response (201 Created)**: Patient object.

### `GET /api/patients/{patient_nbr}`
Retrieve a specific patient's details.
* **Response (200 OK)**: Patient object.
* **Response (404 Not Found)**: `{"detail": "Patient '99887766' not found."}`

### `PUT /api/patients/{patient_nbr}`
Update demographic fields of an existing patient.
* **Request Body**:
```json
{
  "race": "Hispanic",
  "gender": "Female"
}
```
* **Response (200 OK)**: Updated Patient object.

### `DELETE /api/patients/{patient_nbr}`
Delete a patient record and cascaded hospital encounters.
* **Response (204 No Content)**: Empty body.

---

## 🏥 3. Encounter Management Endpoints

### `GET /api/encounters`
Retrieve paginated hospital encounter records with search and readmission filtering.
* **Query Parameters**:
  * `page` (int, default=1)
  * `limit` (int, default=20)
  * `search` (string, optional) — searches `patient_nbr`, `medical_specialty`, `diag_1`
  * `readmitted` (string, optional) — filter by `'<30'`, `'>30'`, `'NO'`
* **Response (200 OK)**:
```json
{
  "total": 101766,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "encounter_id": 2278392,
      "patient_nbr": "8222157",
      "time_in_hospital": 1,
      "num_lab_procedures": 41,
      "num_procedures": 0,
      "num_medications": 1,
      "medical_specialty": "Pediatrics-Endocrinology",
      "readmitted": "NO"
    }
  ]
}
```

### `POST /api/encounters`
Create a new hospital encounter.
* **Request Body**:
```json
{
  "encounter_id": 9999991,
  "patient_nbr": "8222157",
  "time_in_hospital": 3,
  "num_lab_procedures": 45,
  "num_procedures": 1,
  "num_medications": 14,
  "medical_specialty": "InternalMedicine",
  "readmitted": "NO"
}
```
* **Response (201 Created)**: Encounter object.

### `PUT /api/encounters/{encounter_id}`
Update clinical fields of an encounter.
* **Response (200 OK)**: Updated Encounter object.

### `DELETE /api/encounters/{encounter_id}`
Delete an encounter record.
* **Response (204 No Content)**: Empty body.

---

## 📈 4. Healthcare Operational Analytics Endpoints

### `GET /api/analytics/summary`
Retrieve high-level operational KPIs.
* **Response (200 OK)**:
```json
{
  "total_patients": 71518,
  "total_encounters": 101766,
  "readmission_rate_pct": 46.09,
  "avg_length_of_stay_days": 4.4,
  "avg_num_medications": 16.02,
  "avg_lab_procedures": 43.1
}
```

### `GET /api/analytics/readmissions`
Retrieve breakdown of readmission categories.
* **Response (200 OK)**:
```json
[
  { "category": "NO", "count": 54864, "percentage": 53.91 },
  { "category": ">30", "count": 35545, "percentage": 34.93 },
  { "category": "<30", "count": 11357, "percentage": 11.16 }
]
```

### `GET /api/analytics/length-of-stay`
Retrieve encounter distribution by length of stay in days.
* **Response (200 OK)**:
```json
[
  { "days": 1, "count": 14208 },
  { "days": 2, "count": 17224 },
  { "days": 3, "count": 17756 },
  { "days": 4, "count": 13924 }
]
```

### `GET /api/analytics/demographics`
Retrieve patient demographic distributions by race and gender.
