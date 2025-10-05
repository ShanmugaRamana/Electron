# tests/test_view_sample_data.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from db_handler.connect import get_db_connection

def view_sample_data(num_rows=5):
  
    print(f"Fetching first {num_rows} rows from 'power_data'...")
    conn = None
    try:
        conn = get_db_connection()
        query = f"SELECT * FROM power_data ORDER BY reading_date LIMIT {num_rows};"
        df = pd.read_sql_query(query, conn)
        
        print("\n--- Sample Data: power_data ---")
        if df.empty:
            print("The table is empty.")
        else:
            print(df.to_string())
        print("--------------------------------")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    view_sample_data()