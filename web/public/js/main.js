document.addEventListener('DOMContentLoaded', () => {
  // Add a preload class to the body to prevent animations on page load
  document.body.classList.add('preload');

  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('sidebar-toggle');
  const mainContent = document.querySelector('.main-content');

  // Function to set the sidebar state without animation on load
  const setInitialSidebarState = () => {
    if (localStorage.getItem('sidebarOpen') === 'false') {
      sidebar.classList.add('closed');
      mainContent.classList.add('sidebar-closed');
      toggleBtn.classList.remove('toggled');
    } else {
      sidebar.classList.remove('closed');
      mainContent.classList.remove('sidebar-closed');
      toggleBtn.classList.add('toggled');
    }
  };

  // Set the initial state immediately
  setInitialSidebarState();
  
  // Remove the preload class after a tiny delay to re-enable animations
  setTimeout(() => {
    document.body.classList.remove('preload');
  }, 10);


  // Add the click event listener for toggling
  toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('closed');
    mainContent.classList.toggle('sidebar-closed');
    toggleBtn.classList.toggle('toggled');

    // Save state to localStorage
    localStorage.setItem('sidebarOpen', !sidebar.classList.contains('closed'));
  });
});