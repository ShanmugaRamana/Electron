# tests/test_view_schema.py
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_handler.connect import get_db_connection

def view_table_schema():
    """
    Connects to the database and prints the schema of the 'power_data' table.
    """
    print("Fetching schema for table 'power_data'...")
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # This query gets column info from the standard information_schema
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'power_data';
            """)
            columns = cur.fetchall()
            
            print("\n--- Table Schema: power_data ---")
            for col in columns:
                print(f"  - Column: {col[0]:<25} | Type: {col[1]}")
            print("----------------------------------")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        if conn:
            conn.close()

# --- Main execution block ---
if __name__ == "__main__":
    view_table_schema()