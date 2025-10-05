# predictionModel/main.py
import sys
import os
import pandas as pd

# --- Add dataPipeline to the Python path ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_pipeline_path = os.path.join(project_root, 'dataPipeline')
sys.path.append(data_pipeline_path)

from data_loader.loader import fetch_power_data
from models.prophet_model import train_and_forecast
from db_writer.writer import create_wide_forecast_table, insert_wide_forecast_data
from db_handler.connect import get_db_connection

# --- Configuration ---
COLUMNS_TO_FORECAST = [
    "tneb_campus_htsc_91", "tneb_new_stp_htsc_178", "solar_generation",
    "diesel_generation", "biogas_generation", "staff_quarters_util",
    "academic_blocks_util", "hostels_util", "chiller_plant_util",
    "stp_util", "total_consumption"
]
FORECAST_PERIOD_DAYS = 3740

def main():
    print("--- Starting Wide Forecast Pipeline ---")
    
    all_forecasts = {}
    last_historical_date = None

    for column in COLUMNS_TO_FORECAST:
        print(f"\n--- Processing Column: {column} ---")
        
        data_df = fetch_power_data(column)
        
        if data_df is not None and not data_df.empty:
            if last_historical_date is None:
                last_historical_date = pd.to_datetime(data_df['ds'].max())

            model, forecast = train_and_forecast(data_df, periods=FORECAST_PERIOD_DAYS)
            all_forecasts[column] = forecast[['ds', 'yhat']]
        else:
            print(f"Skipping {column} due to data loading error.")

    if not all_forecasts:
        print("No forecasts were generated. Halting.")
        return

    print("\n--- Merging all forecasts into a single table ---")
    
    first_metric_name = list(all_forecasts.keys())[0]
    final_df = all_forecasts[first_metric_name].copy()
    final_df.rename(columns={'yhat': f'{first_metric_name}_pred', 'ds': 'reading_date'}, inplace=True)
    
    for metric_name, forecast_df in all_forecasts.items():
        if metric_name == first_metric_name:
            continue
        merged_df = forecast_df[['ds', 'yhat']].rename(columns={'yhat': f'{metric_name}_pred'})
        final_df = pd.merge(final_df, merged_df, left_on='reading_date', right_on='ds', how='inner')
        final_df.drop('ds', axis=1, inplace=True)

    future_df = final_df[final_df['reading_date'] > last_historical_date].copy()
    
    future_df['month'] = future_df['reading_date'].dt.strftime('%B')
    
    cols = future_df.columns.tolist()
    cols.insert(1, cols.pop(cols.index('month')))
    future_df = future_df[cols]

    print(f"Successfully created a wide table with {len(future_df)} future dates.")
    print("Sample of the final wide table:")
    print(future_df.head())

    conn = None
    try:
        conn = get_db_connection()
        if conn:
            create_wide_forecast_table(conn, COLUMNS_TO_FORECAST)
            insert_wide_forecast_data(conn, future_df)
    except Exception as e:
        print(f"❌ An error occurred during database operations: {e}")
    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")
            
    print("\n--- Wide Forecast Pipeline Finished ---")

if __name__ == '__main__':
    main()