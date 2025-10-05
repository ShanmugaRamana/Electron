from fastapi import APIRouter, Depends, HTTPException, Query
from ..schemas.power import ForecastDataPoint
from ..db.database import get_db
import psycopg2
from psycopg2.extras import DictCursor
from datetime import date, timedelta

router = APIRouter()

# --- THIS IS THE MISSING DICTIONARY ---
# Whitelist of all forecastable columns in the database
ALLOWED_METRICS = [
    "total_consumption_pred", "solar_generation_pred",
    "tneb_campus_htsc_91_pred", "tneb_new_stp_htsc_178_pred", "diesel_generation_pred",
    "biogas_generation_pred", "staff_quarters_util_pred", "academic_blocks_util_pred",
    "hostels_util_pred", "chiller_plant_util_pred", "stp_util_pred"
]
# We'll calculate net_grid_import_pred, so it's not in the direct query list
# ------------------------------------


# This is the last date of your actual, historical data
HISTORICAL_DATA_CUTOFF = date(2025, 6, 30)

@router.get("/forecasts/metric/", response_model=list[ForecastDataPoint])
def get_forecast_for_metric(
    start_date: date,
    end_date: date,
    metric_name: str = Query(..., description="The name of the metric column to forecast"),
    db: psycopg2.extensions.connection = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    # Handle the calculated metric 'net_grid_import_pred' separately
    if metric_name == 'net_grid_import_pred':
        query = """
            SELECT 
                reading_date, 
                (total_consumption_pred - (solar_generation_pred + diesel_generation_pred + biogas_generation_pred)) AS prediction
            FROM forecast_data_wide
            WHERE reading_date BETWEEN %s AND %s
            ORDER BY reading_date ASC;
        """
        params = (start_date, end_date)
    # For all other direct metrics, validate against the whitelist
    elif metric_name not in ALLOWED_METRICS:
        raise HTTPException(status_code=400, detail=f"Invalid metric name requested: {metric_name}")
    else:
        query = f'SELECT reading_date, "{metric_name}" AS prediction FROM forecast_data_wide WHERE reading_date BETWEEN %s AND %s ORDER BY reading_date ASC;'
        params = (start_date, end_date)

    results = []
    
    # Combined logic for fetching data
    # Case 1: The entire requested range is HISTORICAL
    if end_date <= HISTORICAL_DATA_CUTOFF:
        historical_metric = metric_name.replace('_pred', '')
        # Special handling for calculated metric in historical data
        if metric_name == 'net_grid_import_pred':
            hist_query = """
                SELECT 
                    reading_date, 
                    (total_consumption - (solar_generation + diesel_generation + biogas_generation)) AS prediction
                FROM power_data
                WHERE reading_date BETWEEN %s AND %s
                ORDER BY reading_date ASC;
            """
        else:
            hist_query = f'SELECT reading_date, "{historical_metric}" AS prediction FROM power_data WHERE reading_date BETWEEN %s AND %s ORDER BY reading_date ASC;'
        
        with db.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(hist_query, (start_date, end_date))
            for row in cur.fetchall():
                results.append({**dict(row), "type": "historical"})

    # Case 2 & 3: The range is PREDICTED or SPANS both
    else:
        # Fetch historical part if the range starts in the past
        if start_date <= HISTORICAL_DATA_CUTOFF:
            historical_metric = metric_name.replace('_pred', '')
            if metric_name == 'net_grid_import_pred':
                hist_query = """
                    SELECT reading_date, (total_consumption - (solar_generation + diesel_generation + biogas_generation)) AS prediction
                    FROM power_data WHERE reading_date BETWEEN %s AND %s ORDER BY reading_date ASC;
                """
            else:
                hist_query = f'SELECT reading_date, "{historical_metric}" AS prediction FROM power_data WHERE reading_date BETWEEN %s AND %s ORDER BY reading_date ASC;'

            with db.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(hist_query, (start_date, HISTORICAL_DATA_CUTOFF))
                for row in cur.fetchall():
                    results.append({**dict(row), "type": "historical"})
        
        # Fetch predicted part
        pred_start_date = max(start_date, HISTORICAL_DATA_CUTOFF + timedelta(days=1))
        
        with db.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, (pred_start_date, end_date))
            for row in cur.fetchall():
                results.append({**dict(row), "type": "predicted"})

    return results