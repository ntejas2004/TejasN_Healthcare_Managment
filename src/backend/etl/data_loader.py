import os
import pandas as pd
from sqlalchemy import text
import sys

# Ensure backend folder is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import engine


def load_cleaned_data_to_mysql(cleaned_dir):
    """
    Loads cleaned CSV files into MySQL database tables using SQLAlchemy engine.
    Ensures referential integrity: ID Mappings -> Patients -> Encounters.
    """
    patients_file = os.path.join(cleaned_dir, 'cleaned_patients.csv')
    encounters_file = os.path.join(cleaned_dir, 'cleaned_encounters.csv')
    mappings_file = os.path.join(cleaned_dir, 'cleaned_id_mappings.csv')

    for fpath in [patients_file, encounters_file, mappings_file]:
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Required cleaned data file not found: {fpath}")

    print("Beginning MySQL data loading process...")

    with engine.connect() as conn:
        # Disable foreign key checks temporarily for bulk load performance
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        conn.commit()

        # 1. Load ID Mappings
        print("Loading ID mappings into MySQL...")
        mappings_df = pd.read_csv(mappings_file)
        if not mappings_df.empty:
            # Check existing count
            existing_maps = conn.execute(text("SELECT COUNT(*) FROM id_mappings")).scalar()
            if existing_maps == 0:
                mappings_df.to_sql(
                    'id_mappings',
                    con=engine,
                    if_exists='append',
                    index=False,
                    chunksize=1000
                )
                print(f"Inserted {len(mappings_df)} ID mappings.")
            else:
                print(f"ID mappings table already contains {existing_maps} records. Skipping duplicate load.")

        # 2. Load Patients
        print("Loading Patients into MySQL...")
        patients_df = pd.read_csv(patients_file, low_memory=False)
        # Convert NaN to None for SQL null compatibility
        patients_df = patients_df.where(pd.notnull(patients_df), None)
        patients_df['patient_nbr'] = patients_df['patient_nbr'].astype(str)

        existing_patients = conn.execute(text("SELECT COUNT(*) FROM patients")).scalar()
        if existing_patients == 0:
            patients_df.to_sql(
                'patients',
                con=engine,
                if_exists='append',
                index=False,
                chunksize=5000
            )
            print(f"Inserted {len(patients_df)} unique patient records.")
        else:
            print(f"Patients table already contains {existing_patients} records. Skipping duplicate load.")

        # 3. Load Encounters
        print("Loading Encounters into MySQL...")
        encounters_df = pd.read_csv(encounters_file, low_memory=False)
        encounters_df = encounters_df.where(pd.notnull(encounters_df), None)
        encounters_df['patient_nbr'] = encounters_df['patient_nbr'].astype(str)

        existing_encounters = conn.execute(text("SELECT COUNT(*) FROM encounters")).scalar()
        if existing_encounters == 0:
            encounters_df.to_sql(
                'encounters',
                con=engine,
                if_exists='append',
                index=False,
                chunksize=5000
            )
            print(f"Inserted {len(encounters_df)} encounter records.")
        else:
            print(f"Encounters table already contains {existing_encounters} records. Skipping duplicate load.")

        # Re-enable foreign key checks
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        conn.commit()

    print("MySQL data loading completed successfully!")


if __name__ == "__main__":
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    CLEANED_DIR = os.path.join(BASE_DIR, 'data', 'cleaned')
    load_cleaned_data_to_mysql(CLEANED_DIR)
