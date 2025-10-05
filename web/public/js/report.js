document.addEventListener('DOMContentLoaded', () => {
  const reportForm = document.getElementById('report-form');
  const metricsGrid = document.querySelector('.metrics-grid');
  
  // This list should match the metrics available in your backend
  const allMetrics = [
    "Total Consumption", 
    "Total Generation", 
    "Net Grid Import", 
    "TNEB Campus HTSC-91",
    "TNEB New STP HTSC-178", 
    "Solar Generation", 
    "Diesel Generation", 
    "Biogas Generation",
    "Staff Quarters Util", 
    "Academic Blocks Util", 
    "Hostels Util", 
    "Chiller Plant Util", 
    "STP Util"
  ];

  // Dynamically create the checkboxes for the metrics
  function populateMetrics() {
    allMetrics.forEach(metric => {
      const item = document.createElement('div');
      item.classList.add('metric-item');
      
      const checkboxId = metric.toLowerCase().replace(/\s+/g, '-');
      
      item.innerHTML = `
        <input type="checkbox" id="${checkboxId}" name="metrics" value="${metric}">
        <label for="${checkboxId}">${metric}</label>
      `;
      metricsGrid.appendChild(item);
    });
  }

  populateMetrics();

  // Handle form submission
  reportForm.addEventListener('submit', async (event) => {
    event.preventDefault(); // Prevent the form from reloading the page
    
    const statusArea = document.getElementById('report-status-area');
    const statusMessage = document.getElementById('status-message');
    const downloadLink = document.getElementById('download-link');

    // 1. Show "Generating..." status to the user
    statusArea.style.display = 'block';
    statusMessage.textContent = 'Generating your report... Please wait.';
    downloadLink.classList.add('disabled');
    downloadLink.removeAttribute('href');
    
    // 2. Gather all selected options from the form
    const formData = new FormData(reportForm);
    const selectedOptions = {
      startDate: formData.get('start-date'),
      endDate: formData.get('end-date'),
      metrics: formData.getAll('metrics'),
      format: formData.get('format'),
    };

    try {
      // 3. Send the options to the backend API
      const response = await fetch('http://127.0.0.1:8000/api/v1/reports/generate/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(selectedOptions)
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Report generation failed on the server.');
      }

      // 4. Handle the file download response
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      const filename = `report_${selectedOptions.startDate}_to_${selectedOptions.endDate}.${selectedOptions.format}`;
      downloadLink.setAttribute('href', url);
      downloadLink.setAttribute('download', filename);

      // 5. Update the UI to show the report is ready
      statusMessage.textContent = 'Your report is ready for download!';
      downloadLink.classList.remove('disabled');

    } catch (error) {
      statusMessage.textContent = `Error: ${error.message}`;
      console.error('Report generation error:', error);
    }
  });
});