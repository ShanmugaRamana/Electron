from pydantic import BaseModel
from datetime import date

class KpiData(BaseModel):
    today_date: date
    next_day_date: date
    total_consumption_pred: float | None = None
    total_generation_pred: float | None = None
    net_grid_import_pred: float | None = None
    next_day_forecast: float | None = None

# Renamed from HistoricalDataPoint to reflect it can be forecast data
class ChartDataPoint(BaseModel):
    reading_date: date
    total_consumption_pred: float | None = None

class BreakdownData(BaseModel):
    name: str
    value: float

# Updated the response model to use the new names
class TodaysOverviewResponse(BaseModel):
    kpis: KpiData
    forecast_trend: list[ChartDataPoint]
    utilization_breakdown: list[BreakdownData]
    intake_breakdown: list[BreakdownData]

class ReportRequest(BaseModel):
    startDate: date
    endDate: date
    metrics: list[str]
    format: str

# ... (keep all your existing classes)

# ... (keep all your other classes)

class ForecastDataPoint(BaseModel):
    reading_date: date
    prediction: float | None = None
    type: str # NEW: To identify data as 'historical' or 'predicted'