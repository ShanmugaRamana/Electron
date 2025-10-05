# main.py

import pandas as pd
from db_handler.connect import get_db_connection
from db_handler.manage_db import create_power_data_table, insert_data_from_df

# --- Configuration ---
CSV_FILE_PATH = 'cleanedData/data.csv'

def main():
    """Main function to run the data pipeline."""
    print("--- Starting Data to PostgreSQL Pipeline ---")
    
    # Step 1: Connect to the database
    conn = get_db_connection()
    if not conn:
        print("Halting execution due to connection failure.")
        return

    try:
        # Step 2: Create the table if it doesn't exist
        create_power_data_table(conn)
        
        # Step 3: Read data from the CSV file
        print(f"Reading data from '{CSV_FILE_PATH}'...")
        df = pd.read_csv(CSV_FILE_PATH)
        
        # Step 4: Insert data into the database
        insert_data_from_df(conn, df)
        
    except FileNotFoundError:
        print(f"❌ Error: The file '{CSV_FILE_PATH}' was not found.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
    finally:
        # Step 5: Always close the connection
        if conn:
            conn.close()
            print("Database connection closed.")
            
    print("--- Pipeline Finished ---")

if __name__ == '__main__':
    main()