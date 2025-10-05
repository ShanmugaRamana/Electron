import sys
import os
import pandas as pd

# Add dataPipeline to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_pipeline_path = os.path.join(project_root, 'dataPipeline')
sys.path.append(data_pipeline_path)

from db_handler.connect import get_db_connection

def view_sample_forecast_data(num_rows=5):
    """Connects to the DB and prints a sample of rows from the forecast table."""
    print(f"Fetching first {num_rows} rows from 'forecast_data_wide'...")
    conn = None
    try:
        conn = get_db_connection()
        query = f"SELECT * FROM forecast_data_wide ORDER BY reading_date LIMIT {num_rows};"
        df = pd.read_sql_query(query, conn)
        
        print("\n--- Sample Data: forecast_data_wide ---")
        if df.empty:
            print("The table is empty or does not exist.")
        else:
            print(df.to_string())
        print("--------------------------------------")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    view_sample_forecast_data()