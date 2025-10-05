from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, Response
from ..schemas.power import ReportRequest
from ..db.database import get_db
import psycopg2
import pandas as pd
import io
from fpdf import FPDF

router = APIRouter()

# Whitelist of allowed columns
ALLOWED_METRICS = {
    "Total Consumption": "total_consumption_pred",
    "Total Generation": None,
    "Net Grid Import": None,
    "TNEB Campus HTSC-91": "tneb_campus_htsc_91_pred",
    "TNEB New STP HTSC-178": "tneb_new_stp_htsc_178_pred",
    "Solar Generation": "solar_generation_pred",
    "Diesel Generation": "diesel_generation_pred",
    "Biogas Generation": "biogas_generation_pred",
    "Staff Quarters Util": "staff_quarters_util_pred",
    "Academic Blocks Util": "academic_blocks_util_pred",
    "Hostels Util": "hostels_util_pred",
    "Chiller Plant Util": "chiller_plant_util_pred",
    "STP Util": "stp_util_pred"
}

# Helper class to create a PDF with a table
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Power Prediction Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def create_table_from_df(self, df):
        self.add_page(orientation='L')
        self.set_font('Arial', 'B', 8)
        
        header = list(df.columns)
        available_width = self.w - 2 * self.l_margin
        col_width = available_width / len(header) if header else 10

        for h in header:
            self.cell(col_width, 10, str(h), 1)
        self.ln()

        self.set_font('Arial', '', 8)
        for index, row in df.iterrows():
            # Use multi_cell for better text wrapping if needed, but cell is fine for numbers
            for item in row:
                self.cell(col_width, 10, str(item), 1)
            self.ln()

@router.post("/reports/generate/")
def generate_report(request: ReportRequest, db: psycopg2.extensions.connection = Depends(get_db)):
    
    # ... (Logic for building db_columns, query, and fetching df is unchanged) ...
    db_columns = ["reading_date", "month", "total_consumption_pred", "solar_generation_pred", "diesel_generation_pred", "biogas_generation_pred"]
    for metric in request.metrics:
        if metric in ALLOWED_METRICS and ALLOWED_METRICS[metric] is not None:
            db_columns.append(ALLOWED_METRICS[metric])
    db_columns = list(dict.fromkeys(db_columns))
    query = f"""
        SELECT {', '.join(f'"{col}"' for col in db_columns)} 
        FROM forecast_data_wide
        WHERE reading_date BETWEEN %s AND %s
        ORDER BY reading_date;
    """
    df = pd.read_sql_query(query, db, params=(request.startDate, request.endDate))
    if df.empty:
        raise HTTPException(status_code=404, detail="No data found for the selected date range.")
    
    # ... (Logic for calculating derived metrics and renaming columns is unchanged) ...
    if "Total Generation" in request.metrics or "Net Grid Import" in request.metrics:
        df["Total Generation"] = df["solar_generation_pred"] + df["diesel_generation_pred"] + df["biogas_generation_pred"]
    if "Net Grid Import" in request.metrics:
        df["Net Grid Import"] = df["total_consumption_pred"] - df["Total Generation"]
    column_rename_map = {v: k for k, v in ALLOWED_METRICS.items() if v is not None}
    df.rename(columns=column_rename_map, inplace=True)
    final_column_list = ["reading_date", "month"] + request.metrics
    columns_to_keep = [col for col in final_column_list if col in df.columns]
    df_final = df[columns_to_keep]

    # Generate the report in the requested format
    if request.format == 'csv':
        stream = io.StringIO()
        df_final.to_csv(stream, index=False)
        media_type = "text/csv"
        filename = f"report_{request.startDate}_to_{request.endDate}.csv"
        return StreamingResponse(iter([stream.getvalue()]), media_type=media_type, headers={"Content-Disposition": f"attachment; filename={filename}"})

    elif request.format == 'xlsx':
        stream = io.BytesIO()
        df_final.to_excel(stream, index=False, sheet_name='Report')
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"report_{request.startDate}_to_{request.endDate}.xlsx"
        return StreamingResponse(iter([stream.getvalue()]), media_type=media_type, headers={"Content-Disposition": f"attachment; filename={filename}"})

    elif request.format == 'pdf':
        pdf = PDF()
        pdf.create_table_from_df(df_final)
        
        # --- THIS IS THE DEFINITIVE FIX ---
        # The output of pdf.output() can be a bytearray.
        # We must explicitly cast it to 'bytes' to ensure the Response object handles it correctly.
        pdf_bytes = bytes(pdf.output())
        # ----------------------------------
        
        media_type = "application/pdf"
        filename = f"report_{request.startDate}_to_{request.endDate}.pdf"
        return Response(content=pdf_bytes, media_type=media_type, headers={"Content-Disposition": f"attachment; filename={filename}"})

    else:
        raise HTTPException(status_code=400, detail="Invalid format selected.")