import os
import sys
import time
import json

# Add project root and backend to python path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

from etl.data_cleaner import clean_healthcare_data
from etl.data_loader import load_cleaned_data_to_mysql


def run_etl_pipeline():
    """
    Orchestrates the full end-to-end ETL flow:
    Raw CSV extraction -> Pandas cleaning/validation -> MySQL loading -> Execution summary export.
    """
    start_time = time.time()
    print("==================================================")
    print("STARTING HEALTHCARE DATA ETL PIPELINE")
    print("==================================================")

    data_base = os.path.join(BASE_DIR, 'src', 'data') if os.path.exists(os.path.join(BASE_DIR, 'src', 'data')) else os.path.join(BASE_DIR, 'data')
    raw_data_path = os.path.join(data_base, 'raw', 'diabetic_data.csv')
    raw_mapping_path = os.path.join(data_base, 'raw', 'IDS_mapping.csv')
    cleaned_dir = os.path.join(data_base, 'cleaned')
    processed_dir = os.path.join(data_base, 'processed')

    # Step 1: Cleaning & Transformation
    print("\n[STEP 1/3] Executing Data Extraction and Cleaning...")
    patients_df, encounters_df, mappings_df = clean_healthcare_data(
        raw_data_path, raw_mapping_path, cleaned_dir
    )

    # Step 2: Database Loading
    print("\n[STEP 2/3] Loading Cleaned Data into MySQL Database...")
    load_cleaned_data_to_mysql(cleaned_dir)

    # Step 3: Summarize & Export Metadata
    print("\n[STEP 3/3] Generating ETL Summary Statistics...")
    elapsed_time = round(time.time() - start_time, 2)
    
    summary = {
        "status": "SUCCESS",
        "execution_time_seconds": elapsed_time,
        "patients_processed": len(patients_df),
        "encounters_processed": len(encounters_df),
        "mappings_processed": len(mappings_df),
        "cleaned_data_directory": cleaned_dir,
        "processed_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    os.makedirs(processed_dir, exist_ok=True)
    summary_path = os.path.join(processed_dir, 'etl_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=4)

    print(f"ETL Summary exported to: {summary_path}")
    print("\n==================================================")
    print(f"ETL PIPELINE COMPLETED SUCCESSFULLY IN {elapsed_time} SECONDS")
    print("==================================================")
    return summary


if __name__ == "__main__":
    run_etl_pipeline()
