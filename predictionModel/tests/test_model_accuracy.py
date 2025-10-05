import sys
import os
import pandas as pd

# --- FIX: Add the parent 'predictionModel' directory to the path ---
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
prediction_model_path = os.path.join(project_root, 'predictionModel')
data_pipeline_path = os.path.join(project_root, 'dataPipeline')
sys.path.append(prediction_model_path)
sys.path.append(data_pipeline_path)
# -----------------------------------------------------------------

from data_loader.loader import fetch_power_data
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics

# --- Configuration ---
METRIC_TO_TEST = "total_consumption"
INITIAL_TRAIN_PERIOD = "90 days"
FORECAST_HORIZON = "30 days"
CUTOFF_PERIOD = "15 days"

def test_model_accuracy():
    """
    Performs cross-validation to measure the model's forecast accuracy.
    """
    print(f"--- Starting Accuracy Test for '{METRIC_TO_TEST}' ---")
    
    df = fetch_power_data(METRIC_TO_TEST)
    if df is None or len(df) < 120:
        print("❌ Not enough historical data to perform a reliable accuracy test.")
        return

    model = Prophet()
    model.fit(df)

    print("Running cross-validation... (This may take a moment)")
    df_cv = cross_validation(model, initial=INITIAL_TRAIN_PERIOD, period=CUTOFF_PERIOD, horizon=FORECAST_HORIZON)
    
    df_p = performance_metrics(df_cv)

    print("\n--- Model Performance Metrics ---")
    print(df_p[['horizon', 'mape', 'rmse', 'mae']].head())
    
    avg_mape = df_p['mape'].mean() * 100
    print(f"\nOn average, the model's 30-day forecast has a {avg_mape:.2f}% error (MAPE).")
    
    # --- NEW LINES ---
    accuracy = 100 - avg_mape
    print(f"✅ This means the model's accuracy is approximately {accuracy:.2f}%.")
    # -----------------
    
    print("---------------------------------")


if __name__ == "__main__":
    test_model_accuracy()