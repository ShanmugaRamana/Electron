// Import required modules
const express = require('express');
const path = require('path');

// Create an Express application
const app = express();
const port = 3000;

// --- Middlewares ---
// Serve static files (CSS, JS, images) from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// Set EJS as the templating engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// --- Routes ---
// Each route renders a page and passes the current page name for active tab styling
app.get('/', (req, res) => {
  res.render('index', { title: 'Overview', currentPage: 'overview' });
});

app.get('/forecasting', (req, res) => {
  res.render('forecasting', { title: 'Forecasting', currentPage: 'forecasting' });
});

app.get('/comparison', (req, res) => {
  res.render('comparison', { title: 'Comparison', currentPage: 'comparison' });
});

app.get('/report', (req, res) => {
  res.render('report', { title: 'Report', currentPage: 'report' });
});

// Start the server
app.listen(port, () => {
  console.log(`🚀 Server is running at http://localhost:${port}`);
});