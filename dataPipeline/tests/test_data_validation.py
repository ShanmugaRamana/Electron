# tests/test_data_validation.py
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_handler.connect import get_db_connection

def test_for_null_values_in_critical_columns():
    """
    Ensures that critical columns like 'reading_date' do not contain NULLs.
    """
    print("\nRunning test: test_for_null_values_in_critical_columns...")
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM power_data WHERE reading_date IS NULL;")
            null_count = cur.fetchone()[0]
            assert null_count == 0, f"Found {null_count} null values in 'reading_date' column."
            print("✅ PASS: No nulls found in critical columns.")
    except Exception as e:
        print(f"❌ FAIL: {e}")
    finally:
        if conn:
            conn.close()

def test_total_consumption_is_positive():
    """
    Validates that the 'total_consumption' column only contains non-negative values.
    """
    print("\nRunning test: test_total_consumption_is_positive...")
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM power_data WHERE total_consumption < 0;")
            negative_value_count = cur.fetchone()[0]
            assert negative_value_count == 0, f"Found {negative_value_count} records with negative consumption."
            print("✅ PASS: All consumption values are non-negative.")
    except Exception as e:
        print(f"❌ FAIL: {e}")
    finally:
        if conn:
            conn.close()

# --- Main execution block ---
if __name__ == "__main__":
    print("--- Starting Data Validation Tests ---")
    test_for_null_values_in_critical_columns()
    test_total_consumption_is_positive()
    print("\n--- Finished Data Validation Tests ---")