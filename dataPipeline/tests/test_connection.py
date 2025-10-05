import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_handler.connect import get_db_connection

def test_database_connection():
    """
    Tests if a connection to the database can be successfully established.
    """
    print("Running test: test_database_connection...")
    conn = None
    try:
        conn = get_db_connection()
        assert conn is not None, "Connection object should not be None."
        print("✅ PASS: Database connection successful.")
    except Exception as e:
        print(f"❌ FAIL: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("--- Starting Connection Test ---")
    test_database_connection()
    print("--- Finished Connection Test ---")