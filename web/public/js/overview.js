document.addEventListener('DOMContentLoaded', () => {
  fetchDashboardData();
});

// Helper function to format dates consistently
const formatDate = (dateString, options = { timeZone: 'UTC', month: 'long', day: 'numeric' }) => 
  new Date(dateString).toLocaleDateString(undefined, options);

async function fetchDashboardData() {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/v1/dashboard/overview/');
    if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || `HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();

    updateKpiCards(data.kpis);
    renderMainChart(data.forecast_trend);
    renderUtilizationPieChart(data.utilization_breakdown);
    renderIntakeBarChart(data.intake_breakdown);

  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    document.querySelector('.main-content').innerHTML = `<h1>Error</h1><p>Could not load dashboard data: ${error.message}</p><p>This might be because there is no prediction available for today's date in the database.</p>`;
  }
}

function updateKpiCards(kpis) {
  document.getElementById('kpi-today-date').textContent = formatDate(kpis.today_date, { month: 'long', day: 'numeric', year: 'numeric' });
  document.getElementById('kpi-next-day-date').textContent = formatDate(kpis.next_day_date);
  document.getElementById('kpi-total-consumption').textContent = `${Math.round(kpis.total_consumption_pred)} kWh`;
  document.getElementById('kpi-total-generation').textContent = `${Math.round(kpis.total_generation_pred)} kWh`;
  document.getElementById('kpi-net-grid-import').textContent = `${Math.round(kpis.net_grid_import_pred)} kWh`;
  document.getElementById('kpi-next-day-forecast').textContent = kpis.next_day_forecast ? `${Math.round(kpis.next_day_forecast)} kWh` : '--';
}

function renderMainChart(forecastTrend) {
  const ctx = document.getElementById('main-chart-area').getContext('2d');
  
  if(!forecastTrend || forecastTrend.length === 0) return;

  // Data is already in ascending (future) order from the API
  const labels = forecastTrend.map(d => formatDate(d.reading_date, { month: 'short', day: 'numeric' }));

  // Update the date range subtitle
  const startDate = formatDate(forecastTrend[0].reading_date, { month: 'short', day: 'numeric' });
  const endDate = formatDate(forecastTrend[forecastTrend.length - 1].reading_date, { month: 'short', day: 'numeric' });
  document.getElementById('main-chart-dates').textContent = `(${startDate} - ${endDate})`;

  if (window.myMainChart) window.myMainChart.destroy();

  window.myMainChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
          label: 'Predicted Consumption (kWh)',
          data: forecastTrend.map(d => d.total_consumption_pred),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          fill: true,
          tension: 0.4,
      }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        scales: { 
            y: { beginAtZero: true, grid: { color: '#e9ecef' } },
            x: { grid: { display: false } }
        },
        plugins: { legend: { position: 'top' } }
    }
  });
}

function renderUtilizationPieChart(utilizationData) {
  const ctx = document.getElementById('utilization-pie-chart').getContext('2d');
  if (window.myPieChart) window.myPieChart.destroy();
  window.myPieChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
          labels: utilizationData.map(d => d.name),
          datasets: [{
              label: 'Predicted Utilization (kWh)',
              data: utilizationData.map(d => d.value),
              backgroundColor: ['#ff6384','#36a2eb','#ffce56','#4bc0c0','#9966ff'],
              borderWidth: 2,
              borderColor: '#fff'
          }]
      },
      options: { 
          responsive: true, 
          maintainAspectRatio: true,
          aspectRatio: 1.2,
          plugins: { 
              legend: { 
                  position: 'right',
                  align: 'center',
                  labels: {
                      font: {
                          size: 13
                      },
                      boxWidth: 18,
                      boxHeight: 18,
                      padding: 12,
                      usePointStyle: false
                  }
              }
          },
          layout: {
              padding: {
                  left: 0,
                  right: 15,
                  top: 10,
                  bottom: 10
              }
          },
          cutout: '55%'
      }
  });
}

function renderIntakeBarChart(intakeData) {
    const ctx = document.getElementById('intake-bar-chart').getContext('2d');
    if (window.myBarChart) window.myBarChart.destroy();
    window.myBarChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: intakeData.map(d => d.name),
            datasets: [{
                label: 'Predicted Intake (kWh)',
                data: intakeData.map(d => d.value),
                backgroundColor: 'rgba(75, 192, 192, 0.8)'
            }]
        },
        options: { 
            indexAxis: 'y', 
            responsive: true, 
            maintainAspectRatio: false, 
            plugins: { legend: { display: false } } 
        }
    });
}