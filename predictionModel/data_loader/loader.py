import os
import sys
import pandas as pd

# --- Add dataPipeline to the Python path ---
# This allows us to import from the db_handler module
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_pipeline_path = os.path.join(project_root, 'dataPipeline')
sys.path.append(data_pipeline_path)
# ---------------------------------------------

from dotenv import find_dotenv, load_dotenv
from db_handler.connect import get_db_connection # This import works because of the path modification above

# Find and load the .env file from the dataPipeline directory
dotenv_path = find_dotenv(os.path.join(data_pipeline_path, '.env'))
load_dotenv(dotenv_path=dotenv_path)

def fetch_power_data(target_column):
    """
    Fetches data from the database and prepares it for Prophet.
    
    Args:
        target_column (str): The name of the column to be used as the 'y' value.

    Returns:
        pd.DataFrame: A DataFrame with 'ds' and 'y' columns, or None on error.
    """
    print(f"Fetching data for target column: {target_column}...")
    conn = None
    try:
        conn = get_db_connection()
        # Ensure column names with spaces/special characters are quoted
        query = f'SELECT reading_date, "{target_column}" FROM power_data ORDER BY reading_date;'
        df = pd.read_sql_query(query, conn)
        
        # Prophet requires columns to be named 'ds' and 'y'
        df.rename(columns={'reading_date': 'ds', target_column: 'y'}, inplace=True)
        
        print(f"✅ Successfully fetched {len(df)} records.")
        return df
    except Exception as e:
        print(f"❌ Failed to fetch data: {e}")
        return None
    finally:
        if conn:
            conn.close()