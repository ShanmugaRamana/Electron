from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import data, reports, forecasts 

app = FastAPI(
    title="Power Intake and Utilization Prediction API",
    description="An API to serve historical and predicted power data.",
    version="1.0.0"
)

# --- NEW: Add CORS Middleware ---
# This list contains the URLs that are allowed to make requests to your API
origins = [
    "http://localhost:3000", # The origin for your Node.js frontend
    # You can add other origins here if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)
# -----------------------------

# Include the routes from the data.py file
app.include_router(data.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1") # <-- Add this line
app.include_router(forecasts.router, prefix="/api/v1") # <-- Add this line

@app.get("/")
def read_root():
    return {"message": "Welcome! Navigate to /docs for API documentation."}