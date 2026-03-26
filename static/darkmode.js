// Dark mode toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check for saved theme preference or default to light mode
    const currentTheme = localStorage.getItem('theme') || 'light';
    const html = document.documentElement;

    if (currentTheme === 'dark') {
        html.setAttribute('data-bs-theme', 'dark');
    }

    // Create theme toggle button
    const themeToggle = document.createElement('button');
    themeToggle.className = 'theme-toggle';
    themeToggle.innerHTML = currentTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    themeToggle.title = currentTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
    themeToggle.setAttribute('aria-label', currentTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode');

    // Insert toggle button in navbar if it exists
    const navbarNav = document.querySelector('.navbar-nav.ms-auto');
    if (navbarNav) {
        const li = document.createElement('li');
        li.className = 'nav-item';
        li.appendChild(themeToggle);
        navbarNav.insertBefore(li, navbarNav.firstChild);
    } else {
        // If no navbar, add to the top-right corner of the page
        themeToggle.style.position = 'fixed';
        themeToggle.style.top = '20px';
        themeToggle.style.right = '20px';
        themeToggle.style.zIndex = '1050';
        document.body.appendChild(themeToggle);
    }

    // Toggle theme function
    function toggleTheme() {
        const currentTheme = html.getAttribute('data-bs-theme');
        if (currentTheme === 'dark') {
            html.removeAttribute('data-bs-theme');
            localStorage.setItem('theme', 'light');
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
            themeToggle.title = 'Switch to Dark Mode';
            themeToggle.setAttribute('aria-label', 'Switch to Dark Mode');
        } else {
            html.setAttribute('data-bs-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            themeToggle.title = 'Switch to Light Mode';
            themeToggle.setAttribute('aria-label', 'Switch to Light Mode');
        }
    }

    // Add click event listener
    themeToggle.addEventListener('click', toggleTheme);
});