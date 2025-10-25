"""
Flask API Backend for Food Delivery Time Prediction
This script loads the trained models and provides an API endpoint
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import tensorflow as tf
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Load models and preprocessors
print("Loading models...")
try:
    with open('gbr_model.pkl', 'rb') as f:
        gbr_model = pickle.load(f)
    
    lstm_model = tf.keras.models.load_model('lstm_model.h5')
    
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    
    with open('label_encoders.pkl', 'rb') as f:
        encoders = pickle.load(f)
    
    with open('feature_columns.pkl', 'rb') as f:
        feature_columns = pickle.load(f)
    
    print("✓ All models loaded successfully!")
except Exception as e:
    print(f"Error loading models: {e}")
    print("Make sure all .pkl and .h5 files are in the same directory")

def prepare_features(data):
    """
    Prepare input features for prediction
    """
    # Encode categorical variables
    restaurant_encoded = encoders['restaurant'].transform([data['restaurant']])[0]
    city_encoded = encoders['city'].transform([data['city']])[0]
    cuisine_encoded = encoders['cuisine'].transform([data['cuisine']])[0]
    day_type_encoded = encoders['day_type'].transform([data['day_type']])[0]
    meal_type_encoded = encoders['meal_type'].transform([data['meal_type']])[0]
    weather_encoded = encoders['weather'].transform([data['weather']])[0]
    traffic_encoded = encoders['traffic'].transform([data['traffic']])[0]
    
    # Create feature array
    features = {
        'distance_km': data['distance'],
        'order_hour': data['order_hour'],
        'num_items': data['num_items'],
        'preparation_time_min': data['prep_time'],
        'restaurant_rating': data['restaurant_rating'],
        'delivery_partner_experience_months': data['partner_experience'],
        'order_value_inr': data['order_value'],
        'restaurant_encoded': restaurant_encoded,
        'city_encoded': city_encoded,
        'cuisine_encoded': cuisine_encoded,
        'day_type_encoded': day_type_encoded,
        'meal_type_encoded': meal_type_encoded,
        'weather_encoded': weather_encoded,
        'traffic_encoded': traffic_encoded,
        'is_peak_hour': 1 if data['order_hour'] in [13, 14, 20, 21] else 0,
        'is_night': 1 if data['order_hour'] >= 22 or data['order_hour'] <= 6 else 0
    }
    
    # Convert to array in correct order
    feature_array = np.array([[features[col] for col in feature_columns]])
    
    return feature_array

def calculate_confidence(distance, weather, traffic, order_hour):
    """
    Calculate prediction confidence based on various factors
    """
    confidence = 90  # Base confidence
    
    # Reduce confidence for extreme conditions
    if weather in ['Heavy Rain']:
        confidence -= 15
    elif weather in ['Rain']:
        confidence -= 8
    
    if traffic in ['Very High']:
        confidence -= 10
    elif traffic in ['High']:
        confidence -= 5
    
    if distance > 10:
        confidence -= 8
    elif distance > 7:
        confidence -= 4
    
    # Peak hours are less predictable
    if order_hour in [13, 14, 20, 21]:
        confidence -= 3
    
    return max(confidence, 60)  # Minimum 60% confidence

@app.route('/predict', methods=['POST'])
def predict():
    """
    API endpoint for delivery time prediction
    """
    try:
        data = request.json
        
        # Get current time info
        now = datetime.now()
        order_hour = data.get('order_hour', now.hour)
        day_type = 'Weekend' if now.weekday() >= 5 else 'Weekday'
        
        # Determine meal type based on hour
        if 6 <= order_hour < 11:
            meal_type = 'Breakfast'
        elif 11 <= order_hour < 16:
            meal_type = 'Lunch'
        elif 16 <= order_hour < 19:
            meal_type = 'Snacks'
        else:
            meal_type = 'Dinner'
        
        # Prepare input data
        input_data = {
            'restaurant': data.get('restaurant', 'Faasos'),
            'city': data.get('city', 'Mumbai'),
            'cuisine': data.get('cuisine', 'North Indian'),
            'distance': float(data.get('distance', 5.0)),
            'order_hour': order_hour,
            'num_items': int(data.get('num_items', 2)),
            'prep_time': int(data.get('prep_time', 15)),
            'restaurant_rating': float(data.get('restaurant_rating', 4.2)),
            'partner_experience': int(data.get('partner_experience', 12)),
            'order_value': int(data.get('order_value', 450)),
            'weather': data.get('weather', 'Clear'),
            'traffic': data.get('traffic', 'Medium'),
            'day_type': day_type,
            'meal_type': meal_type
        }
        
        # Prepare features
        features = prepare_features(input_data)
        
        # Scale features for LSTM
        features_scaled = scaler.transform(features)
        features_lstm = features_scaled.reshape((features_scaled.shape[0], 1, features_scaled.shape[1]))
        
        # Get predictions from both models
        gbr_prediction = gbr_model.predict(features)[0]
        lstm_prediction = lstm_model.predict(features_lstm, verbose=0)[0][0]
        
        # Ensemble: weighted average (GBR 60%, LSTM 40%)
        final_prediction = (gbr_prediction * 0.6) + (lstm_prediction * 0.4)
        final_prediction = round(float(final_prediction))
        
        # Calculate confidence
        confidence = calculate_confidence(
            input_data['distance'],
            input_data['weather'],
            input_data['traffic'],
            order_hour
        )
        
        # Calculate factor impacts
        weather_impacts = {
            'Clear': 'Minimal',
            'Cloudy': 'Low',
            'Hot': 'Low',
            'Rain': 'Moderate',
            'Heavy Rain': 'High'
        }
        
        traffic_impacts = {
            'Low': 'Minimal',
            'Medium': 'Moderate',
            'High': 'Significant',
            'Very High': 'Very High'
        }
        
        distance_factor = 'High' if input_data['distance'] > 7 else 'Medium' if input_data['distance'] > 4 else 'Low'
        is_peak = order_hour in [13, 14, 20, 21]
        
        # Prepare response
        response = {
            'success': True,
            'estimated_time': final_prediction,
            'confidence': confidence,
            'gbr_prediction': round(float(gbr_prediction)),
            'lstm_prediction': round(float(lstm_prediction)),
            'factors': {
                'weather_impact': weather_impacts[input_data['weather']],
                'traffic_impact': traffic_impacts[input_data['traffic']],
                'distance_factor': distance_factor,
                'peak_hour': 'Yes (+15%)' if is_peak else 'No'
            },
            'route_info': {
                'distance': input_data['distance'],
                'restaurant': input_data['restaurant'],
                'city': input_data['city']
            },
            'timestamp': now.isoformat()
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'models_loaded': True,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def home():
    """
    Home endpoint with API documentation
    """
    return jsonify({
        'message': 'Food Delivery Time Prediction API',
        'version': '1.0',
        'endpoints': {
            '/predict': 'POST - Get delivery time prediction',
            '/health': 'GET - Health check'
        },
        'required_fields': {
            'restaurant': 'string',
            'city': 'string',
            'distance': 'float (km)',
            'num_items': 'int',
            'weather': 'string (Clear/Cloudy/Hot/Rain/Heavy Rain)',
            'traffic': 'string (Low/Medium/High/Very High)',
            'order_value': 'int (INR)'
        },
        'optional_fields': {
            'cuisine': 'string',
            'prep_time': 'int (minutes)',
            'restaurant_rating': 'float',
            'partner_experience': 'int (months)',
            'order_hour': 'int (0-23)'
        }
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Food Delivery Time Prediction API")
    print("="*50)
    print("\nStarting server on http://localhost:5000")
    print("\nEndpoints:")
    print("  GET  /        - API documentation")
    print("  GET  /health  - Health check")
    print("  POST /predict - Get delivery time prediction")
    print("\n" + "="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)