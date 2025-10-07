// Traffic Management System Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Smooth scrolling for navigation links
    setupSmoothScrolling();
    
    // Load dashboard data
    loadDashboardData();
    
    // Setup event listeners
    setupEventListeners();
}

function setupSmoothScrolling() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function setupEventListeners() {
    const ctaButton = document.querySelector('.cta-button');
    
    if (ctaButton) {
        ctaButton.addEventListener('click', function() {
            // Scroll to dashboard section
            const dashboard = document.querySelector('#dashboard');
            if (dashboard) {
                dashboard.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    }
}

function loadDashboardData() {
    // Simulate loading current traffic data
    setTimeout(() => {
        updateCurrentTraffic();
    }, 1000);
    
    // Simulate loading predictions
    setTimeout(() => {
        updatePredictions();
    }, 1500);
    
    // Simulate loading alerts
    setTimeout(() => {
        updateAlerts();
    }, 2000);
}

function updateCurrentTraffic() {
    const currentTrafficElement = document.getElementById('current-traffic');
    if (currentTrafficElement) {
        const trafficData = {
            level: 'Moderate',
            vehicles: 1250,
            avgSpeed: '35 km/h'
        };
        
        currentTrafficElement.innerHTML = `
            <div class="traffic-info">
                <p><strong>Level:</strong> ${trafficData.level}</p>
                <p><strong>Vehicles:</strong> ${trafficData.vehicles}</p>
                <p><strong>Avg Speed:</strong> ${trafficData.avgSpeed}</p>
            </div>
        `;
    }
}

function updatePredictions() {
    const predictionsElement = document.getElementById('predictions');
    if (predictionsElement) {
        const predictions = [
            'Heavy traffic expected at 5:00 PM',
            'Clear roads predicted for next 2 hours',
            'Construction delay on Main St'
        ];
        
        predictionsElement.innerHTML = `
            <ul class="predictions-list">
                ${predictions.map(prediction => `<li>${prediction}</li>`).join('')}
            </ul>
        `;
    }
}

function updateAlerts() {
    const alertsElement = document.getElementById('alerts');
    if (alertsElement) {
        const alerts = [
            'Road closure on Highway 101',
            'Accident reported on 5th Avenue'
        ];
        
        if (alerts.length > 0) {
            alertsElement.innerHTML = `
                <ul class="alerts-list">
                    ${alerts.map(alert => `<li class="alert-item">${alert}</li>`).join('')}
                </ul>
            `;
        } else {
            alertsElement.innerHTML = '<p>No current alerts</p>';
        }
    }
}

// API Integration functions (to be connected with backend)
async function fetchTrafficData() {
    try {
        // This would connect to your backend API
        const response = await fetch('/api/traffic/current');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching traffic data:', error);
        return null;
    }
}

async function fetchPredictions() {
    try {
        // This would connect to your backend API
        const response = await fetch('/api/predictions');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching predictions:', error);
        return null;
    }
}

// Utility functions
function formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString();
}

function formatTrafficLevel(level) {
    const levels = {
        1: 'Light',
        2: 'Moderate', 
        3: 'Heavy',
        4: 'Severe'
    };
    return levels[level] || 'Unknown';
}
