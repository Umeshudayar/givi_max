// Add this JavaScript to your frontend to connect with the Flask backend
// Replace the predictDeliveryTime() function in index.html with this version

const API_BASE_URL = 'http://localhost:5000';  // Change this to your deployed backend URL

async function predictDeliveryTime() {
    // Show loading state
    const predictBtn = document.querySelector('.predict-btn');
    const originalText = predictBtn.textContent;
    predictBtn.textContent = 'Predicting...';
    predictBtn.disabled = true;
    
    // Get form values
    const restaurant = document.getElementById('restaurant').value;
    const city = document.getElementById('city').value;
    const distance = parseFloat(document.getElementById('distance').value);
    const orderValue = parseInt(document.getElementById('orderValue').value);
    const numItems = parseInt(document.getElementById('numItems').value);
    const weather = document.getElementById('weather').value;
    const traffic = document.getElementById('traffic').value;
    
    // Get cuisine based on restaurant (simplified mapping)
    const restaurantCuisine = {
        'Biryani Blues': 'Biryani',
        'Faasos': 'Fast Food',
        'Behrouz Biryani': 'Biryani',
        'Oven Story Pizza': 'Italian',
        'The Bowl Company': 'Healthy',
        'Lunch Box': 'North Indian',
        'Mandarin Oak': 'Chinese',
        'Firangi Bake': 'Italian',
        'EatFit': 'Healthy',
        'Box8': 'North Indian'
    };
    
    // Prepare request payload
    const payload = {
        restaurant: restaurant,
        city: city,
        distance: distance,
        num_items: numItems,
        weather: weather,
        traffic: traffic,
        order_value: orderValue,
        cuisine: restaurantCuisine[restaurant] || 'North Indian',
        prep_time: 12 + (numItems * 2),  // Estimate prep time
        restaurant_rating: 4.2 + Math.random() * 0.5,  // Random rating 4.2-4.7
        partner_experience: Math.floor(Math.random() * 36) + 6  // 6-42 months
    };
    
    try {
        // Call the prediction API
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error('API request failed');
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || 'Prediction failed');
        }
        
        // Hide initial message and show results
        document.getElementById('initialMessage').style.display = 'none';
        document.getElementById('predictionResult').classList.add('active');
        
        // Update time display with animation
        animateValue('timeValue', 0, result.estimated_time, 1000);
        
        // Update confidence with animation
        setTimeout(() => {
            document.getElementById('confidenceFill').style.width = result.confidence + '%';
            document.getElementById('confidenceText').textContent = result.confidence + '% Confidence';
        }, 500);
        
        // Update route distance
        document.getElementById('routeDistance').textContent = distance.toFixed(1);
        
        // Update factors from API response
        document.getElementById('weatherImpact').textContent = result.factors.weather_impact;
        document.getElementById('trafficImpact').textContent = result.factors.traffic_impact;
        document.getElementById('distanceFactor').textContent = result.factors.distance_factor;
        document.getElementById('peakHour').textContent = result.factors.peak_hour;
        
        // Initialize/update map
        updateMap(distance, city);
        
        // Log model predictions for debugging
        console.log('Prediction Results:', {
            final: result.estimated_time,
            gbr: result.gbr_prediction,
            lstm: result.lstm_prediction,
            confidence: result.confidence
        });
        
    } catch (error) {
        console.error('Prediction error:', error);
        alert('Failed to get prediction. Please check if the backend server is running on ' + API_BASE_URL);
        
        // Fallback to client-side prediction if API fails
        console.log('Falling back to client-side prediction...');
        const currentHour = new Date().getHours();
        const fallbackPrediction = calculateDeliveryTime(distance, weather, traffic, currentHour, numItems);
        
        document.getElementById('initialMessage').style.display = 'none';
        document.getElementById('predictionResult').classList.add('active');
        
        animateValue('timeValue', 0, fallbackPrediction.time, 1000);
        
        setTimeout(() => {
            document.getElementById('confidenceFill').style.width = (fallbackPrediction.confidence - 10) + '%';
            document.getElementById('confidenceText').textContent = (fallbackPrediction.confidence - 10) + '% Confidence (Offline Mode)';
        }, 500);
        
        document.getElementById('routeDistance').textContent = distance.toFixed(1);
        document.getElementById('weatherImpact').textContent = fallbackPrediction.weatherImpact;
        document.getElementById('trafficImpact').textContent = fallbackPrediction.trafficImpact;
        document.getElementById('distanceFactor').textContent = fallbackPrediction.distanceFactor;
        document.getElementById('peakHour').textContent = fallbackPrediction.peakHour;
        
        updateMap(distance, city);
        
    } finally {
        // Reset button state
        predictBtn.textContent = originalText;
        predictBtn.disabled = false;
    }
}

// Fallback function for offline mode (same as before)
function calculateDeliveryTime(distance, weather, traffic, hour, items) {
    let baseTime = distance * 4;
    let prepTime = 12 + (items * 2);
    
    const weatherMultipliers = {
        'Clear': 1.0,
        'Cloudy': 1.05,
        'Hot': 1.1,
        'Rain': 1.3,
        'Heavy Rain': 1.6
    };
    
    const trafficMultipliers = {
        'Low': 1.0,
        'Medium': 1.2,
        'High': 1.5,
        'Very High': 1.8
    };
    
    const isPeakHour = [12, 13, 14, 19, 20, 21].includes(hour);
    
    baseTime *= weatherMultipliers[weather];
    baseTime *= trafficMultipliers[traffic];
    
    if (isPeakHour) {
        baseTime *= 1.15;
    }
    
    let totalTime = Math.round(prepTime + baseTime);
    
    let confidence = 85;
    if (weather === 'Heavy Rain') confidence -= 10;
    if (traffic === 'Very High') confidence -= 8;
    if (distance > 10) confidence -= 5;
    
    const weatherImpacts = {
        'Clear': 'Minimal',
        'Cloudy': 'Low',
        'Hot': 'Low',
        'Rain': 'Moderate',
        'Heavy Rain': 'High'
    };
    
    const trafficImpacts = {
        'Low': 'Minimal',
        'Medium': 'Moderate',
        'High': 'Significant',
        'Very High': 'Very High'
    };
    
    return {
        time: totalTime,
        confidence: confidence,
        weatherImpact: weatherImpacts[weather],
        trafficImpact: trafficImpacts[traffic],
        distanceFactor: distance > 7 ? 'High' : distance > 4 ? 'Medium' : 'Low',
        peakHour: isPeakHour ? 'Yes (+15%)' : 'No'
    };
}

// Helper function to animate number counting
function animateValue(id, start, end, duration) {
    const element = document.getElementById(id);
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.round(current);
    }, 16);
}

// Map update function
function updateMap(distance, city) {
    const cityCoords = {
        'Mumbai': [19.0760, 72.8777],
        'Delhi': [28.6139, 77.2090],
        'Bangalore': [12.9716, 77.5946],
        'Hyderabad': [17.3850, 78.4867],
        'Pune': [18.5204, 73.8567],
        'Chennai': [13.0827, 80.2707],
        'Kolkata': [22.5726, 88.3639]
    };
    
    const center = cityCoords[city] || [19.0760, 72.8777];
    
    if (!map) {
        map = L.map('map').setView(center, 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
    } else {
        map.setView(center, 13);
    }
    
    if (routeLayer) {
        map.removeLayer(routeLayer);
    }
    
    const startPoint = center;
    const endPoint = [
        center[0] + (Math.random() - 0.5) * distance * 0.015,
        center[1] + (Math.random() - 0.5) * distance * 0.015
    ];
    
    const restaurantIcon = L.divIcon({
        html: '<div style="background: #ff6b6b; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">🏪</div>',
        className: '',
        iconSize: [30, 30]
    });
    
    const deliveryIcon = L.divIcon({
        html: '<div style="background: #4ecdc4; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">📍</div>',
        className: '',
        iconSize: [30, 30]
    });
    
    L.marker(startPoint, {icon: restaurantIcon}).addTo(map)
        .bindPopup('<b>Restaurant Location</b>');
    L.marker(endPoint, {icon: deliveryIcon}).addTo(map)
        .bindPopup('<b>Delivery Location</b>');
    
    routeLayer = L.polyline([startPoint, endPoint], {
        color: '#667eea',
        weight: 4,
        opacity: 0.7,
        dashArray: '10, 10'
    }).addTo(map);
    
    map.fitBounds([startPoint, endPoint], {padding: [50, 50]});
}

// Test backend connection on page load
async function testBackendConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✓ Backend connected successfully');
            return true;
        }
    } catch (error) {
        console.warn('⚠ Backend not available. Using offline mode.');
        console.log('Make sure Flask server is running on', API_BASE_URL);
        return false;
    }
}

// Initialize
let map;
let routeLayer;

// Test connection when page loads
window.addEventListener('DOMContentLoaded', () => {
    testBackendConnection();
    
    // Add form submit handler
    document.getElementById('predictionForm').addEventListener('submit', function(e) {
        e.preventDefault();
        predictDeliveryTime();
    });
});