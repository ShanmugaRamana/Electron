from fastapi import FastAPI

# Create an instance of the FastAPI application
app = FastAPI(
    title="Power Intake and Utilization Prediction API",
    description="An API to serve historical and predicted power data.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": "Welcome to the Power Prediction API!"}