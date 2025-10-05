document.addEventListener('DOMContentLoaded', () => {
  const startDateInput = document.getElementById('start-date');
  const endDateInput = document.getElementById('end-date');
  const mapShapes = document.querySelectorAll('.campus-map-svg .building, .campus-map-svg .building-group');
  const chartTitle = document.getElementById('total-consumption-title');

  let forecastChartInstance = null;
  let currentMetric = 'total_consumption_pred';
  let currentMetricName = 'Total Consumption';

  function initialize() {
    // Default to a range that spans historical and future data
    const startDate = new Date('2025-06-24');
    const endDate = new Date('2025-07-07');
    startDateInput.value = startDate.toISOString().split('T')[0];
    endDateInput.value = endDate.toISOString().split('T')[0];
    
    // Add event listeners
    [startDateInput, endDateInput].forEach(el => el.addEventListener('change', () => updateChartWithMetric(currentMetric, currentMetricName)));

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
    // ... (logic to update visual feedback and get dates is the same as before) ...
    
    try {
      const apiUrl = `/api/v1/forecasts/metric/?start_date=${startDateInput.value}&end_date=${endDateInput.value}&metric_name=${metric}`;
      const response = await fetch(`http://127.0.0.1:8000${apiUrl}`);
      if (!response.ok) throw new Error('Failed to fetch data');
      const data = await response.json();
      
      renderForecastChart(data);
    } catch (error) {
      console.error("Error updating chart:", error);
    }
  }
  
  function renderForecastChart(data) {
    const ctx = document.getElementById('total-consumption-chart').getContext('2d');
    if (forecastChartInstance) forecastChartInstance.destroy();

    // Separate data into historical and predicted arrays
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
            borderColor: 'rgb(54, 162, 235)', // Blue for actual data
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            fill: true,
            tension: 0.3,
          },
          {
            label: `Predicted ${currentMetricName}`,
            data: predictedPoints.map(d => ({ x: d.reading_date, y: d.prediction })),
            borderColor: 'rgb(255, 99, 132)', // Red for predicted data
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderDash: [5, 5], // Make the prediction line dashed
            fill: true,
            tension: 0.3,
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