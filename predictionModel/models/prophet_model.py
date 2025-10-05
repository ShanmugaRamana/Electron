# models/prophet_model.py
from prophet import Prophet

def train_and_forecast(df, periods=30, freq='D'):
    """
    Trains a Prophet model and returns a forecast.

    Args:
        df (pd.DataFrame): DataFrame with 'ds' and 'y' columns.
        periods (int): Number of future periods to forecast.
        freq (str): Frequency of the forecast ('D' for day, 'M' for month).

    Returns:
        tuple: A tuple containing the trained model and the forecast DataFrame.
    """
    print("Training Prophet model...")
    # You can add seasonality here if you know your data patterns
    # e.g., model = Prophet(weekly_seasonality=True)
    model = Prophet()
    model.fit(df)
    
    print(f"Generating forecast for the next {periods} {freq}s...")
    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)
    
    print("✅ Forecast complete.")
    return model, forecast