import sys
import os

# Add dataPipeline to the Python path to find the db_handler module
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_pipeline_path = os.path.join(project_root, 'dataPipeline')
sys.path.append(data_pipeline_path)

from db_handler.connect import get_db_connection

def check_forecast_date_range():
    """Connects to the DB and finds the min and max dates in the forecast_data_wide table."""
    print("Finding the date range of your predicted data in 'forecast_data_wide'...")
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT MIN(reading_date), MAX(reading_date) FROM forecast_data_wide;")
            result = cur.fetchone()
            
            print("\n--- 'forecast_data_wide' Table Date Range ---")
            if result and result[0] is not None:
                print(f"  Earliest Predicted Date: {result[0]}")
                print(f"  Latest Predicted Date:   {result[1]}")
            else:
                print("  Could not find any data. The table might be empty.")
            print("---------------------------------------------")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_forecast_date_range()