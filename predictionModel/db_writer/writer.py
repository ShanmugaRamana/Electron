# predictionModel/db_writer/writer.py

def create_wide_forecast_table(conn, columns_to_forecast):
    """Dynamically creates a 'wide' table for storing all forecasts."""
    column_definitions = ["reading_date DATE PRIMARY KEY", "month VARCHAR(20)"]
    
    for col in columns_to_forecast:
        column_definitions.append(f'"{col}_pred" FLOAT')
    
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS forecast_data_wide (
        {', '.join(column_definitions)}
    );
    """
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS forecast_data_wide;")
        cur.execute(create_table_query)
        conn.commit()
    print("✅ Table 'forecast_data_wide' is ready.")


def insert_wide_forecast_data(conn, wide_df):
    """Inserts the combined wide forecast DataFrame into the database."""
    print("Inserting wide forecast data into the database...")
    
    # --- THIS IS THE CORRECTED PART ---
    # This now correctly formats each column name with quotes and joins them.
    cols = ", ".join([f'"{c}"' for c in wide_df.columns])
    
    placeholders = ', '.join(['%s'] * len(wide_df.columns))
    
    insert_query = f"INSERT INTO forecast_data_wide ({cols}) VALUES ({placeholders});"
    
    with conn.cursor() as cur:
        for index, row in wide_df.iterrows():
            cur.execute(insert_query, tuple(row))
        conn.commit()
    print(f"✅ Successfully inserted {len(wide_df)} rows into 'forecast_data_wide'.")