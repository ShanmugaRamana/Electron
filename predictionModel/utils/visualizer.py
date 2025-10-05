# utils/visualizer.py
import os

def save_forecast_plots(model, forecast, target_column):
    """
    Generates and saves Prophet's forecast plots to a file.
    """
    output_dir = 'forecast_plots'
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        print(f"Saving plots for {target_column}...")
        # Plot the forecast
        fig1 = model.plot(forecast)
        plot_filename = os.path.join(output_dir, f'{target_column}_forecast.png')
        fig1.savefig(plot_filename)
        
        # Plot the forecast components (trend, seasonality)
        fig2 = model.plot_components(forecast)
        components_filename = os.path.join(output_dir, f'{target_column}_components.png')
        fig2.savefig(components_filename)
        
        print(f"✅ Plots saved to '{output_dir}/'")
    except Exception as e:
        print(f"❌ Could not save plots: {e}")