# db_handler/manage_db.py

import pandas as pd
from datetime import datetime

def create_power_data_table(conn):
    """Creates the power_data table if it does not already exist."""
    # MODIFIED: Removed id and created_at columns
    create_table_query = """
    CREATE TABLE IF NOT EXISTS power_data (
        month VARCHAR(20),
        reading_date DATE,
        tneb_campus_htsc_91 FLOAT,
        tneb_new_stp_htsc_178 FLOAT,
        solar_generation FLOAT,
        diesel_generation FLOAT,
        biogas_generation FLOAT,
        staff_quarters_util FLOAT,
        academic_blocks_util FLOAT,
        hostels_util FLOAT,
        chiller_plant_util FLOAT,
        stp_util FLOAT,
        total_consumption FLOAT
    );
    """
    with conn.cursor() as cur:
        cur.execute(create_table_query)
        conn.commit()
        print("✅ Table 'power_data' is ready.")

# This function does not need to be changed
def insert_data_from_df(conn, df):
    """Inserts data from a pandas DataFrame into the power_data table."""
    insert_query = """
    INSERT INTO power_data (
        month, reading_date, tneb_campus_htsc_91, tneb_new_stp_htsc_178,
        solar_generation, diesel_generation, biogas_generation,
        staff_quarters_util, academic_blocks_util, hostels_util,
        chiller_plant_util, stp_util, total_consumption
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    with conn.cursor() as cur:
        for index, row in df.iterrows():
            standardized_date_str = row['DATE'].replace('.', '/')
            reading_date = datetime.strptime(standardized_date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
            
            data_tuple = (
                row['MONTH'], reading_date, row['TNEB Campus HTSC-91'], row['TNEB New STP HTSC-178'],
                row['Power Generation by Solar Panels'], row['Power Generation by Diesel Engines'],
                row['Power Generation by Biogas Engines'], row['Staff Quarters '], row['Academic blocks '],
                row['Hostels'], row['Chiller plant'], row['STP'], row['Total Consumption (in units)']
            )
            cur.execute(insert_query, data_tuple)
        conn.commit()
        print(f"✅ Successfully inserted {len(df)} rows into the database.")