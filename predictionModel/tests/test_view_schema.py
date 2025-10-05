import sys
import os

# Add dataPipeline to the Python path to find the db_handler module
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_pipeline_path = os.path.join(project_root, 'dataPipeline')
sys.path.append(data_pipeline_path)

from db_handler.connect import get_db_connection

def view_forecast_schema():
    """Connects to the DB and prints the schema of the 'forecast_data_wide' table."""
    print("Fetching schema for table 'forecast_data_wide'...")
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'forecast_data_wide';
            """)
            columns = cur.fetchall()
            
            print("\n--- Table Schema: forecast_data_wide ---")
            for col in columns:
                print(f"  - Column: {col[0]:<30} | Type: {col[1]}")
            print("----------------------------------------")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    view_forecast_schema()