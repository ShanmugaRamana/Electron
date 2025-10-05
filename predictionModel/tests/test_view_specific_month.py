import sys
import os
import pandas as pd

# Add dataPipeline to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_pipeline_path = os.path.join(project_root, 'dataPipeline')
sys.path.append(data_pipeline_path)

from db_handler.connect import get_db_connection

def view_data_for_november_2025(num_rows=5):
    """Connects to the DB and prints a sample of rows from November 2025."""
    print(f"Fetching first {num_rows} rows from November 2025...")
    conn = None
    try:
        conn = get_db_connection()
        
        query = f"""
            SELECT * FROM forecast_data_wide 
            WHERE reading_date BETWEEN '2025-11-01' AND '2025-11-30'
            ORDER BY reading_date 
            LIMIT {num_rows};
        """
        df = pd.read_sql_query(query, conn)
        
        print("\n--- Sample Data for November 2025 ---")
        if df.empty:
            print("No data found for the specified month.")
        else:
            print(df.to_string())
        print("-------------------------------------")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    view_data_for_november_2025()