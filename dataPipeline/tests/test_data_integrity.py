# tests/test_data_integrity.py
import sys
import os

# Add project root to sys.path
# This helps Python find your db_handler module when running the script directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from db_handler.connect import get_db_connection
from datetime import datetime

def test_row_count_matches_csv():
    """
    Tests if the number of rows in the DB table matches the CSV file.
    """
    print("\nRunning test: test_row_count_matches_csv...")
    conn = None
    try:
        df = pd.read_csv('cleanedData/data.csv')
        csv_row_count = len(df)
        
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM power_data;")
            db_row_count = cur.fetchone()[0]
            
            assert csv_row_count == db_row_count, f"Row count mismatch: CSV has {csv_row_count}, DB has {db_row_count}"
            assert db_row_count > 0, "Table is empty."
            print("✅ PASS: Row count matches and table is not empty.")
    except Exception as e:
        print(f"❌ FAIL: {e}")
    finally:
        if conn:
            conn.close()

def test_specific_data_point():
    """
    Picks the first row of the CSV and verifies its values in the database
    by looking it up with the date.
    """
    print("\nRunning test: test_specific_data_point...")
    conn = None
    try:
        df = pd.read_csv('cleanedData/data.csv')
        first_row = df.iloc[0]
        
        # Parse the date from the CSV to use in the lookup
        csv_date_str = first_row['DATE'].replace('.', '/')
        csv_date_obj = datetime.strptime(csv_date_str, '%d/%m/%Y').date()
        
        conn = get_db_connection()
        with conn.cursor() as cur:
            # --- THIS IS THE MODIFIED PART ---
            # Query the database using the date instead of the ID
            sql_query = "SELECT reading_date, total_consumption FROM power_data WHERE reading_date = %s;"
            cur.execute(sql_query, (csv_date_obj,)) # Pass date as a parameter
            result = cur.fetchone()
            # ---------------------------------
            
            assert result is not None, f"No data found in DB for date {csv_date_obj}"
            
            db_date, db_total_consumption = result
            
            assert db_date == csv_date_obj, f"Date mismatch: DB has {db_date}, CSV has {csv_date_obj}"
            assert db_total_consumption == first_row['Total Consumption (in units)'], "Total consumption mismatch"
            print("✅ PASS: Specific data point matches.")
    except Exception as e:
        print(f"❌ FAIL: {e}")
    finally:
        if conn:
            conn.close()

# --- Main execution block ---
if __name__ == "__main__":
    print("--- Starting Data Integrity Tests ---")
    test_row_count_matches_csv()
    test_specific_data_point()
    print("\n--- Finished Data Integrity Tests ---")