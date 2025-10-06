document.addEventListener('DOMContentLoaded', () => {
  const API_BASE_URL = 'http://127.0.0.1:8000';
  
  const horizonSelect = document.getElementById('horizon-select');
  const mapShapes = document.querySelectorAll('.campus-map-svg .building, .campus-map-svg .building-group');
  const chartTitle = document.getElementById('total-consumption-title');

  let forecastChartInstance = null;
  let currentMetric = 'total_consumption_pred';
  let currentMetricName = 'Total Consumption';

  function initialize() {
    // Add event listeners
    horizonSelect.addEventListener('change', () => updateChartWithMetric(currentMetric, currentMetricName));

    mapShapes.forEach(shape => {
      shape.addEventListener('click', () => {
        const metric = shape.dataset.metric;
        const name = shape.dataset.name;
        if (metric && name) {
          updateChartWithMetric(metric, name);
        }
      });
    });

    // Initial chart load
    updateChartWithMetric(currentMetric, currentMetricName);
  }

  async function updateChartWithMetric(metric, name) {
    currentMetric = metric;
    currentMetricName = name;
    
    // Update visual feedback on the map
    mapShapes.forEach(s => s.classList.remove('selected'));
    const selectedShape = document.querySelector(`[data-metric="${metric}"]`);
    if (selectedShape) {
      selectedShape.classList.add('selected');
    }

    // --- NEW: Calculate dates based on dropdown ---
    const daysToForecast = parseInt(horizonSelect.value, 10);
    const today = new Date();
    const futureDate = new Date();
    futureDate.setDate(today.getDate() + daysToForecast - 1); // -1 because we include today

    const startDate = today.toISOString().split('T')[0];
    const endDate = futureDate.toISOString().split('T')[0];
    // ---------------------------------------------
    
    chartTitle.textContent = `${name} Forecast`;
    
    try {
      const apiUrl = `${API_BASE_URL}/api/v1/forecasts/metric/?start_date=${startDate}&end_date=${endDate}&metric_name=${metric}`;
      const response = await fetch(apiUrl);
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to fetch forecast data');
      }
      const data = await response.json();
      
      renderForecastChart(data);
    } catch (error) {
      console.error("Error updating chart:", error);
      chartTitle.textContent = `Error: ${error.message}`;
    }
  }
  
  function renderForecastChart(data) {
    const ctx = document.getElementById('total-consumption-chart').getContext('2d');
    if (forecastChartInstance) forecastChartInstance.destroy();
    
    // Logic to separate historical and predicted data
    const historicalPoints = data.filter(d => d.type === 'historical');
    const predictedPoints = data.filter(d => d.type === 'predicted');
    
    forecastChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.map(d => d.reading_date),
        datasets: [
          {
            label: `Actual ${currentMetricName}`,
            data: historicalPoints.map(d => ({ x: d.reading_date, y: d.prediction })),
            borderColor: 'rgb(54, 162, 235)',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            fill: true, tension: 0.3,
          },
          {
            label: `Predicted ${currentMetricName}`,
            data: predictedPoints.map(d => ({ x: d.reading_date, y: d.prediction })),
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderDash: [5, 5],
            fill: true, tension: 0.3,
          }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: { x: { type: 'time', time: { unit: 'day' } } }
      }
    });
  }

  initialize();
});