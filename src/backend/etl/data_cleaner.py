import os
import pandas as pd
import numpy as np


def parse_ids_mapping(filepath):
    """
    Parses IDS_mapping.csv which contains header sections for:
    - admission_type_id
    - discharge_disposition_id
    - admission_source_id
    """
    if not os.path.exists(filepath):
        print(f"Warning: Mapping file not found at {filepath}")
        return pd.DataFrame()

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f]

    mappings = []
    current_category = None

    for line in lines:
        if not line:
            continue
        parts = line.split(',')
        header_candidate = parts[0].strip()
        
        if header_candidate in ['admission_type_id', 'discharge_disposition_id', 'admission_source_id']:
            current_category = header_candidate
            continue
        
        if current_category and len(parts) >= 2:
            map_id_str = parts[0].strip()
            desc = ','.join(parts[1:]).strip()
            if map_id_str.isdigit():
                mappings.append({
                    'category': current_category,
                    'mapping_id': int(map_id_str),
                    'description': desc if desc else 'Unknown'
                })

    return pd.DataFrame(mappings)


def clean_healthcare_data(raw_data_path, raw_mapping_path, output_dir):
    """
    Cleans raw healthcare data from diabetic_data.csv and IDS_mapping.csv.
    Saves cleaned data to output_dir.
    """
    print(f"Loading raw data from {raw_data_path}...")
    if not os.path.exists(raw_data_path):
        raise FileNotFoundError(f"Raw data file not found at: {raw_data_path}")

    # Load raw CSV
    df = pd.read_csv(raw_data_path)
    initial_count = len(df)
    print(f"Loaded {initial_count} raw encounter records.")

    # 1. Standardize missing values ('?' -> NaN)
    df.replace('?', np.nan, inplace=True)

    # 2. Deduplicate by encounter_id
    df.drop_duplicates(subset=['encounter_id'], keep='first', inplace=True)
    dedup_count = len(df)
    print(f"Deduplicated encounters: {initial_count - dedup_count} duplicates removed.")

    # 3. Clean and convert numeric fields
    numeric_cols = [
        'encounter_id', 'admission_type_id', 'discharge_disposition_id', 
        'admission_source_id', 'time_in_hospital', 'num_lab_procedures', 
        'num_procedures', 'num_medications', 'number_outpatient', 
        'number_emergency', 'number_inpatient', 'number_diagnoses'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 4. Clean string columns
    str_cols = [
        'patient_nbr', 'race', 'gender', 'age', 'weight', 'payer_code', 
        'medical_specialty', 'diag_1', 'diag_2', 'diag_3', 'max_glu_serum', 
        'A1Cresult', 'metformin', 'repaglinide', 'nateglinide', 'chlorpropamide', 
        'glimepiride', 'acetohexamide', 'glipizide', 'glyburide', 'tolbutamide', 
        'pioglitazone', 'rosiglitazone', 'acarbose', 'miglitol', 'troglitazone', 
        'tolazamide', 'examide', 'citoglipton', 'insulin', 'glyburide-metformin', 
        'glipizide-metformin', 'glimepiride-pioglitazone', 'metformin-rosiglitazone', 
        'metformin-pioglitazone', 'change', 'diabetesMed', 'readmitted'
    ]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({'nan': None, 'None': None, '<NA>': None})

    # Convert patient_nbr to string
    df['patient_nbr'] = df['patient_nbr'].astype(str)

    # Standardize column name hyphens to underscores for database compatibility
    rename_dict = {
        'glyburide-metformin': 'glyburide_metformin',
        'glipizide-metformin': 'glipizide_metformin',
        'glimepiride-pioglitazone': 'glimepiride_pioglitazone',
        'metformin-rosiglitazone': 'metformin_rosiglitazone',
        'metformin-pioglitazone': 'metformin_pioglitazone',
        'change': 'med_change'
    }
    df.rename(columns=rename_dict, inplace=True)

    # 5. Extract Patients DataFrame (unique by patient_nbr)
    # Re-order/sort by encounter_id to get latest patient demographics
    df_sorted = df.sort_values(by='encounter_id', ascending=True)
    patients_df = df_sorted[['patient_nbr', 'race', 'gender', 'age', 'weight']].drop_duplicates(
        subset=['patient_nbr'], keep='last'
    )

    # Fill missing values for demographic display
    patients_df['race'] = patients_df['race'].fillna('Unknown')
    patients_df['gender'] = patients_df['gender'].fillna('Unknown')
    patients_df['age'] = patients_df['age'].fillna('Unknown')
    patients_df['weight'] = patients_df['weight'].fillna('Unknown')

    # 6. Extract Encounters DataFrame
    encounter_cols = [
        'encounter_id', 'patient_nbr', 'admission_type_id', 'discharge_disposition_id',
        'admission_source_id', 'time_in_hospital', 'payer_code', 'medical_specialty',
        'num_lab_procedures', 'num_procedures', 'num_medications', 'number_outpatient',
        'number_emergency', 'number_inpatient', 'diag_1', 'diag_2', 'diag_3',
        'number_diagnoses', 'max_glu_serum', 'A1Cresult', 'metformin', 'repaglinide',
        'nateglinide', 'chlorpropamide', 'glimepiride', 'acetohexamide', 'glipizide',
        'glyburide', 'tolbutamide', 'pioglitazone', 'rosiglitazone', 'acarbose',
        'miglitol', 'troglitazone', 'tolazamide', 'examide', 'citoglipton', 'insulin',
        'glyburide_metformin', 'glipizide_metformin', 'glimepiride_pioglitazone',
        'metformin_rosiglitazone', 'metformin_pioglitazone', 'med_change', 'diabetesMed',
        'readmitted'
    ]
    encounters_df = df[encounter_cols].copy()

    # 7. Parse ID Mappings
    mappings_df = parse_ids_mapping(raw_mapping_path)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save cleaned files
    patients_file = os.path.join(output_dir, 'cleaned_patients.csv')
    encounters_file = os.path.join(output_dir, 'cleaned_encounters.csv')
    mappings_file = os.path.join(output_dir, 'cleaned_id_mappings.csv')

    patients_df.to_csv(patients_file, index=False)
    encounters_df.to_csv(encounters_file, index=False)
    mappings_df.to_csv(mappings_file, index=False)

    print(f"Data cleaning complete:")
    print(f"  - Unique Patients: {len(patients_df)} -> {patients_file}")
    print(f"  - Encounters: {len(encounters_df)} -> {encounters_file}")
    print(f"  - ID Mappings: {len(mappings_df)} -> {mappings_file}")

    return patients_df, encounters_df, mappings_df


if __name__ == "__main__":
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    RAW_DATA = os.path.join(BASE_DIR, 'data', 'raw', 'diabetic_data.csv')
    RAW_MAPPING = os.path.join(BASE_DIR, 'data', 'raw', 'IDS_mapping.csv')
    CLEANED_DIR = os.path.join(BASE_DIR, 'data', 'cleaned')

    clean_healthcare_data(RAW_DATA, RAW_MAPPING, CLEANED_DIR)
