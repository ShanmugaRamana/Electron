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

  // State management elements - with null checks
  const initialState = document.getElementById('initial-state');
  const loadingState = document.getElementById('loading-state');
  const successState = document.getElementById('success-state');
  const errorState = document.getElementById('error-state');
  
  const loadingMessage = document.getElementById('loading-message');
  const progressBar = document.getElementById('progress-bar');
  const progressText = document.getElementById('progress-text');
  const downloadLink = document.getElementById('download-link');
  const errorMessage = document.getElementById('error-message');

  // Check if all required elements exist
  if (!initialState || !loadingState || !successState || !errorState || 
      !loadingMessage || !progressBar || !progressText || !downloadLink || !errorMessage) {
    console.error('Required UI elements not found. Please check your HTML structure.');
    return;
  }

  // Progress messages
  const progressMessages = [
    'Connecting to server...',
    'Fetching data from database...',
    'Processing selected metrics...',
    'Generating visualizations...',
    'Compiling report document...',
    'Finalizing your report...'
  ];

  // Function to show specific state
  function showState(state) {
    if (initialState) initialState.style.display = 'none';
    if (loadingState) loadingState.style.display = 'none';
    if (successState) successState.style.display = 'none';
    if (errorState) errorState.style.display = 'none';
    
    if (state) {
      state.style.display = 'block';
    }
  }

  // Function to animate progress animation
  function animateProgress(currentProgress, targetProgress, duration = 1000) {
    if (!progressBar || !progressText) return;
    
    const startProgress = currentProgress;
    const progressDiff = targetProgress - startProgress;
    const startTime = Date.now();

    function update() {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      const currentValue = startProgress + (progressDiff * progress);
      if (progressBar) progressBar.style.width = currentValue + '%';
      if (progressText) progressText.textContent = Math.floor(currentValue) + '%';

      if (progress < 1) {
        requestAnimationFrame(update);
      }
    }

    requestAnimationFrame(update);
  }

  // Function to update loading message based on progress
  function updateLoadingMessage(progress) {
    if (!loadingMessage) return;
    const messageIndex = Math.min(
      Math.floor((progress / 100) * progressMessages.length),
      progressMessages.length - 1
    );
    loadingMessage.textContent = progressMessages[messageIndex];
  }

  // Handle form submission
  reportForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    
    // 1. Show loading state
    showState(loadingState);
    
    // Reset progress
    let currentProgress = 0;
    if (progressBar) progressBar.style.width = '0%';
    if (progressText) progressText.textContent = '0%';
    if (loadingMessage) loadingMessage.textContent = progressMessages[0];
    
    // Start initial progress animation
    animateProgress(0, 20, 500);
    updateLoadingMessage(20);
    
    // 2. Gather all selected options from the form
    const formData = new FormData(reportForm);
    const selectedOptions = {
      startDate: formData.get('start-date'),
      endDate: formData.get('end-date'),
      metrics: formData.getAll('metrics'),
      format: formData.get('format'),
    };

    // Validate metrics selection
    if (selectedOptions.metrics.length === 0) {
      showState(errorState);
      if (errorMessage) {
        errorMessage.textContent = 'Please select at least one metric to include in the report.';
      }
      return;
    }

    try {
      // Animate to 40%
      setTimeout(() => {
        currentProgress = 40;
        animateProgress(20, currentProgress, 800);
        updateLoadingMessage(currentProgress);
      }, 500);

      // 3. Send the options to the backend API
      const response = await fetch('http://127.0.0.1:8000/api/v1/reports/generate/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(selectedOptions)
      });

      // Animate to 70%
      currentProgress = 70;
      animateProgress(40, currentProgress, 1000);
      updateLoadingMessage(currentProgress);

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Report generation failed on the server.');
      }

      // 4. Handle the file download response
      const blob = await response.blob();
      
      // Animate to 90%
      currentProgress = 90;
      animateProgress(70, currentProgress, 500);
      updateLoadingMessage(currentProgress);

      const url = window.URL.createObjectURL(blob);
      const filename = `energy_report_${selectedOptions.startDate}_to_${selectedOptions.endDate}.${selectedOptions.format}`;
      
      // Set download link
      if (downloadLink) {
        downloadLink.setAttribute('href', url);
        downloadLink.setAttribute('download', filename);
      }

      // Complete progress
      animateProgress(90, 100, 300);
      
      // 5. Show success state after a brief delay
      setTimeout(() => {
        showState(successState);
      }, 500);

    } catch (error) {
      // Show error state
      showState(errorState);
      if (errorMessage) {
        errorMessage.textContent = error.message || 'An unexpected error occurred. Please try again.';
      }
      console.error('Report generation error:', error);
    }
  });

  // Handle "Generate Another Report" button
  const generateAnotherBtn = document.getElementById('generate-another-btn');
  if (generateAnotherBtn) {
    generateAnotherBtn.addEventListener('click', () => {
      showState(initialState);
      reportForm.reset();
      
      // Clear download link
      if (downloadLink) {
        downloadLink.removeAttribute('href');
        downloadLink.removeAttribute('download');
      }
    });
  }

  // Handle "Try Again" button
  const retryBtn = document.getElementById('retry-btn');
  if (retryBtn) {
    retryBtn.addEventListener('click', () => {
      showState(initialState);
    });
  }

  // Auto-download on success (optional - comment out if not needed)
  if (downloadLink) {
    downloadLink.addEventListener('click', (e) => {
      if (!downloadLink.hasAttribute('href')) {
        e.preventDefault();
      }
    });
  }
});