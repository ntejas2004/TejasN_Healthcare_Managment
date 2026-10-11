# Healthcare Patient Management System

A full-stack, enterprise-grade Healthcare Patient Management & Operational Analytics System built with Python, Pandas, MySQL, SQLAlchemy, FastAPI, and React + Vite.

---

## 🚀 Key Features

* **Healthcare Data Cleaning & Validation**: Automated extraction from raw healthcare CSVs, standardization of missing values (`?` → `NaN`), record deduplication, and schema validation.
* **Normalized Relational Database**: Structured MySQL database models (`patients`, `encounters`, `id_mappings`) with foreign key constraints, indexes, and cascade integrity.
* **Automated ETL Pipeline**: One-command pipeline orchestrating CSV extraction, Pandas data cleaning, batch MySQL insertion, and JSON metadata generation.
* **FastAPI REST Microservice**: High-performance REST API supporting full CRUD for Patient and Encounter records, pagination, text search, and pre-computed operational analytics.
* **Interactive Swagger UI**: OpenAPI documentation accessible live at `http://127.0.0.1:8000/docs`.
* **React + Vite Dashboard**: Modern responsive UI with interactive KPI scorecards, patient management modal forms, encounter management tables, and dynamic visual analytics using Recharts.

---

## 🛠️ Technology Stack

* **Backend**: Python 3.10+, Pandas, SQLAlchemy, PyMySQL, FastAPI, Uvicorn, Pydantic, `python-dotenv`
* **Database**: MySQL 8.0+
* **Frontend**: React 18, Vite 6, Axios, Recharts, Lucide React
* **Documentation & Presentation**: Markdown, FPDF2, python-pptx

---

## 📂 Project Architecture & Folder Structure

```text
prodapt_final_task/
├── .env
├── .env.example
├── README.md
├── requirements.txt
├── .gitignore
├── API_Documentation.md
├── Dataset_Details.md
├── generate_artifacts.py
├── Healthcare Patient Management System.docx
└── src/
    ├── .venv/
    ├── sql/
    │   └── init.sql
    ├── data/
    │   ├── raw/
    │   │   ├── diabetic_data.csv
    │   │   ├── IDS_mapping.csv
    │   │   └── Healthcare Patient Management System.docx
    │   ├── cleaned/
    │   │   ├── cleaned_patients.csv
    │   │   ├── cleaned_encounters.csv
    │   │   └── cleaned_id_mappings.csv
    │   └── processed/
    │       └── etl_summary.json
    ├── backend/
    │   ├── database.py
    │   ├── models.py
    │   ├── schemas.py
    │   ├── crud.py
    │   ├── main.py
    │   ├── auth.py
    │   ├── seed_users.py
    │   └── etl/
    │       ├── data_cleaner.py
    │       ├── data_loader.py
    │       └── etl_pipeline.py
    └── frontend/
        ├── package.json
        ├── vite.config.js
        ├── index.html
        └── src/
            ├── App.jsx
            ├── main.jsx
            ├── index.css
            ├── api/
            │   └── client.js
            ├── context/
            │   └── AuthContext.jsx
            └── components/
                ├── Navbar.jsx
                ├── Dashboard.jsx
                ├── PatientList.jsx
                ├── EncounterList.jsx
                ├── Analytics.jsx
                └── LoginPage.jsx
```

---

## ⚙️ Installation & Setup Instructions

### 1. Prerequisites
* Python 3.10 or higher
* Node.js v18+ and npm
* MySQL Server running on `127.0.0.1:3306`

### 2. Configure Environment Variables
Copy `.env.example` to `.env` in the root folder and verify your MySQL credentials:

```env
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=healthcare_db
```

### 3. Install Python Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 4. Run the ETL Data Pipeline
Execute the full data extraction, cleaning, and MySQL loading pipeline:
```powershell
python src/backend/etl/etl_pipeline.py
```

---

## 🏃 Running the Complete Application

The application runs locally in **two separate terminal windows**:

### Terminal 1 — Backend (FastAPI Microservice)
```powershell
python -m uvicorn src.backend.main:app --reload --host 127.0.0.1 --port 8000
```
* **API Base URL**: `http://127.0.0.1:8000`
* **Swagger UI Docs**: `http://127.0.0.1:8000/docs`
* **ReDoc Docs**: `http://127.0.0.1:8000/redoc`

### Terminal 2 — Frontend (React + Vite Web Application)
```powershell
cd src/frontend
npm install
npm run dev
```
* **Frontend Web Application**: `http://localhost:5173`
* **Frontend Web Application**: `http://localhost:5173`

---

## 📊 Key Operational Metrics (Empirical Dataset Output)

* **Total Patients Managed**: 71,518 unique patient records
* **Total Encounters Tracked**: 101,766 hospital visits
* **Hospital Readmission Rate**: 46.09% (`>30` days: 34.93%, `<30` days: 11.16%)
* **Average Length of Stay**: 4.40 Days
* **Average Medications per Encounter**: 16.02
* **Average Lab Procedures per Encounter**: 43.10
