from fastapi import APIRouter, Depends, HTTPException
from ..schemas.power import TodaysOverviewResponse
from ..db.database import get_db
import psycopg2
from psycopg2.extras import DictCursor
from datetime import date, timedelta

router = APIRouter()

@router.get("/dashboard/overview/", response_model=TodaysOverviewResponse)
def get_todays_overview(db: psycopg2.extensions.connection = Depends(get_db)):
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    today = date.today()
    tomorrow = today + timedelta(days=1)

    with db.cursor(cursor_factory=DictCursor) as cur:
        # 1. Get today's predicted data for KPIs and breakdowns
        cur.execute("SELECT * FROM forecast_data_wide WHERE reading_date = %s;", (today,))
        todays_pred = cur.fetchone()
        if not todays_pred:
            raise HTTPException(status_code=404, detail=f"No prediction found for today's date: {today}")

        # 2. Get tomorrow's predicted consumption for the KPI card
        cur.execute("SELECT total_consumption_pred FROM forecast_data_wide WHERE reading_date = %s;", (tomorrow,))
        tomorrows_pred = cur.fetchone()

        # 3. Get the next 7 days of PREDICTED data for the main trend chart
        cur.execute("""
            SELECT reading_date, total_consumption_pred FROM forecast_data_wide 
            WHERE reading_date >= CURRENT_DATE 
            ORDER BY reading_date ASC LIMIT 7;
        """)
        forecast_trend = cur.fetchall()

    # 4. Calculate predicted KPIs for today
    total_generation_pred = (todays_pred.get("solar_generation_pred", 0) or 0) + \
                            (todays_pred.get("diesel_generation_pred", 0) or 0) + \
                            (todays_pred.get("biogas_generation_pred", 0) or 0)
    
    net_grid_import_pred = (todays_pred.get("total_consumption_pred", 0) or 0) - total_generation_pred

    kpis = {
        "today_date": today,
        "next_day_date": tomorrow,
        "total_consumption_pred": todays_pred["total_consumption_pred"],
        "total_generation_pred": total_generation_pred,
        "net_grid_import_pred": net_grid_import_pred,
        "next_day_forecast": tomorrows_pred["total_consumption_pred"] if tomorrows_pred else None
    }

    # 5. Prepare breakdown charts based on today's prediction
    utilization_breakdown = [
        {"name": "Staff Quarters", "value": todays_pred["staff_quarters_util_pred"]},
        {"name": "Academic", "value": todays_pred["academic_blocks_util_pred"]},
        {"name": "Hostels", "value": todays_pred["hostels_util_pred"]},
        {"name": "Chiller", "value": todays_pred["chiller_plant_util_pred"]},
        {"name": "STP", "value": todays_pred["stp_util_pred"]},
    ]
    
    intake_breakdown = [
        {"name": "Grid (TNEB)", "value": (todays_pred["tneb_campus_htsc_91_pred"] or 0) + (todays_pred["tneb_new_stp_htsc_178_pred"] or 0)},
        {"name": "Solar", "value": todays_pred["solar_generation_pred"]},
        {"name": "Diesel", "value": todays_pred["diesel_generation_pred"]},
        {"name": "Biogas", "value": todays_pred["biogas_generation_pred"]},
    ]
    
    return {
        "kpis": kpis,
        "forecast_trend": [dict(row) for row in forecast_trend],
        "utilization_breakdown": utilization_breakdown,
        "intake_breakdown": intake_breakdown
    }