import pandas as pd
from prophet import Prophet
import xgboost as xgb
import numpy as np

def create_features(df):
    """
    Creates time series features from a datetime index (ds).
    This now includes lag and rolling window features.
    """
    df = df.copy()
    df['ds'] = pd.to_datetime(df['ds'])
    
    # Time-based features
    df['dayofweek'] = df['ds'].dt.dayofweek
    df['month'] = df['ds'].dt.month
    df['year'] = df['ds'].dt.year
    df['dayofyear'] = df['ds'].dt.dayofyear
    df['weekofyear'] = df['ds'].dt.isocalendar().week.astype(int)
    
    # Lag features (value from 1 and 2 weeks ago)
    df['lag_7'] = df['y'].shift(7)
    df['lag_14'] = df['y'].shift(14)
    
    # Rolling window features
    df['rolling_mean_7'] = df['y'].shift(1).rolling(window=7).mean()
    
    return df

def train_and_forecast(df, periods=30, freq='D'):
    print("--- Starting ADVANCED Hybrid Prophet + XGBoost Model ---")
    df['ds'] = pd.to_datetime(df['ds'])

    # === Step 1: Train Prophet for baseline forecast ===
    print("Step 1: Training Prophet model...")
    prophet_model = Prophet(weekly_seasonality=True)
    prophet_model.fit(df)
    forecast_on_history = prophet_model.predict(df)
    
    # === Step 2: Calculate Prophet's errors (residuals) ===
    print("Step 2: Calculating residuals...")
    df_with_errors = pd.merge(df, forecast_on_history[['ds', 'yhat']], on='ds')
    df_with_errors['error'] = df_with_errors['y'] - df_with_errors['yhat']

    # === Step 3: Train XGBoost to predict the errors using advanced features ===
    print("Step 3: Training XGBoost on residuals with lag/rolling features...")
    df_for_xgb_train = create_features(df_with_errors.copy())
    
    # Drop rows with NaN values created by lag/rolling features
    df_for_xgb_train.dropna(inplace=True)

    FEATURES = ['dayofyear', 'dayofweek', 'month', 'year', 'weekofyear', 'lag_7', 'lag_14', 'rolling_mean_7']
    TARGET = 'error'

    X_train_xgb = df_for_xgb_train[FEATURES]
    y_train_xgb = df_for_xgb_train[TARGET]

    xgb_regressor = xgb.XGBRegressor(n_estimators=500, learning_rate=0.05, max_depth=5, random_state=42)
    xgb_regressor.fit(X_train_xgb, y_train_xgb)
    
    # === Step 4: Make future forecast using a recursive loop ===
    print("Step 4: Making recursive future forecast...")
    future = prophet_model.make_future_dataframe(periods=periods, freq=freq)
    prophet_forecast = prophet_model.predict(future)
    
    future_forecast_only = prophet_forecast[prophet_forecast['ds'] > df['ds'].max()].copy()
    
    # Combine historical and future data to create rolling features
    full_df = pd.concat([df_with_errors, future_forecast_only[['ds']]], ignore_index=True)

    # Loop one day at a time to predict recursively
    for i in range(len(df), len(full_df)):
        # Create features for the single day we are predicting
        temp_df = create_features(full_df.iloc[[i]].copy())
        
        # Manually create lag/rolling features from the (partially filled) full_df
        temp_df['lag_7'] = full_df.loc[i-7, 'y'] if i-7 >= 0 else np.nan
        temp_df['lag_14'] = full_df.loc[i-14, 'y'] if i-14 >= 0 else np.nan
        temp_df['rolling_mean_7'] = full_df.loc[i-7:i-1, 'y'].mean() if i-7 >= 0 else np.nan
        
        # Predict the error for this single day
        features_for_pred = temp_df[FEATURES].values
        predicted_error = xgb_regressor.predict(features_for_pred)
        
        # Add the predicted error to Prophet's baseline forecast
        prophet_base_yhat = prophet_forecast.loc[i, 'yhat']
        final_yhat = prophet_base_yhat + predicted_error[0]
        
        # IMPORTANT: Update the 'y' value in our loop dataframe with the new prediction
        # This makes it available for the next day's lag/rolling calculation
        full_df.loc[i, 'y'] = final_yhat
        
        # Update the final forecast DataFrame
        prophet_forecast.loc[i, 'yhat'] = final_yhat
        prophet_forecast.loc[i, 'yhat_lower'] += predicted_error[0]
        prophet_forecast.loc[i, 'yhat_upper'] += predicted_error[0]

    print("✅ Advanced hybrid forecast complete.")
    return prophet_model, prophet_forecast