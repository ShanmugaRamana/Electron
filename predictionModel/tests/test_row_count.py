import sys
import os

# Add dataPipeline to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_pipeline_path = os.path.join(project_root, 'dataPipeline')
sys.path.append(data_pipeline_path)

from db_handler.connect import get_db_connection

def count_forecast_rows():
    """Connects to the DB and counts the total number of rows in the forecast table."""
    print("Counting total rows in 'forecast_data_wide'...")
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM forecast_data_wide;")
            row_count = cur.fetchone()[0]
            
            print("\n--- Total Rows ---")
            print(f"✅ The table 'forecast_data_wide' contains {row_count} rows.")
            print("------------------")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    count_forecast_rows()