import sys
import os

# Add the parent 'dataPipeline' directory to the Python path
# This allows us to import from the 'db_handler' module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_handler.connect import get_db_connection

def check_date_range():
    """Connects to the DB and finds the min and max dates in the power_data table."""
    print("Finding the date range of your historical data in 'power_data'...")
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT MIN(reading_date), MAX(reading_date) FROM power_data;")
            result = cur.fetchone()
            
            print("\n--- 'power_data' Table Date Range ---")
            if result and result[0] is not None:
                print(f"  Earliest Date: {result[0]}")
                print(f"  Latest Date:   {result[1]}")
            else:
                print("  Could not find any data. The table might be empty.")
            print("-------------------------------------")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_date_range()