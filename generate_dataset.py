import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import math

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Indian cities with actual coordinates
CITIES = {
    'Mumbai': {
        'coords': (19.0760, 72.8777),
        'areas': [
            'Andheri East', 'Bandra West', 'Powai', 'Goregaon', 'Malad', 
            'Borivali', 'Kandivali', 'Dadar', 'Kurla', 'Vile Parle'
        ]
    },
    'Delhi': {
        'coords': (28.6139, 77.2090),
        'areas': [
            'Connaught Place', 'Dwarka', 'Rohini', 'Nehru Place', 'Saket',
            'Lajpat Nagar', 'Karol Bagh', 'Janakpuri', 'Mayur Vihar', 'Vasant Kunj'
        ]
    },
    'Bangalore': {
        'coords': (12.9716, 77.5946),
        'areas': [
            'Koramangala', 'Indiranagar', 'Whitefield', 'HSR Layout', 'Jayanagar',
            'Marathahalli', 'Electronic City', 'BTM Layout', 'JP Nagar', 'Yelahanka'
        ]
    },
    'Hyderabad': {
        'coords': (17.3850, 78.4867),
        'areas': [
            'HITEC City', 'Banjara Hills', 'Jubilee Hills', 'Gachibowli', 'Kukatpally',
            'Secunderabad', 'Madhapur', 'Kondapur', 'Miyapur', 'Uppal'
        ]
    },
    'Pune': {
        'coords': (18.5204, 73.8567),
        'areas': [
            'Hinjewadi', 'Kothrud', 'Viman Nagar', 'Wakad', 'Baner',
            'Hadapsar', 'Aundh', 'Shivaji Nagar', 'Pimpri', 'Chinchwad'
        ]
    },
    'Chennai': {
        'coords': (13.0827, 80.2707),
        'areas': [
            'T Nagar', 'Anna Nagar', 'Velachery', 'Adyar', 'Nungambakkam',
            'Porur', 'Guindy', 'Perungudi', 'Sholinganallur', 'Tambaram'
        ]
    }
}

# Restaurant data with multiple branches
RESTAURANTS = {
    'Biryani Blues': {'cuisine': 'Biryani', 'rating': 4.3, 'prep_time': (15, 25)},
    'Faasos': {'cuisine': 'Fast Food', 'rating': 4.1, 'prep_time': (10, 18)},
    'Behrouz Biryani': {'cuisine': 'Biryani', 'rating': 4.4, 'prep_time': (18, 28)},
    'Oven Story Pizza': {'cuisine': 'Italian', 'rating': 4.2, 'prep_time': (15, 22)},
    'The Bowl Company': {'cuisine': 'Healthy', 'rating': 4.3, 'prep_time': (12, 20)},
    'Lunch Box': {'cuisine': 'North Indian', 'rating': 4.0, 'prep_time': (12, 20)},
    'Mandarin Oak': {'cuisine': 'Chinese', 'rating': 4.2, 'prep_time': (15, 23)},
    'EatFit': {'cuisine': 'Healthy', 'rating': 4.4, 'prep_time': (10, 18)},
    'Box8': {'cuisine': 'North Indian', 'rating': 4.1, 'prep_time': (12, 20)},
    'WarmOven': {'cuisine': 'Italian', 'rating': 4.2, 'prep_time': (15, 22)}
}

# Street name generators
STREET_TYPES = ['Road', 'Street', 'Lane', 'Avenue', 'Marg', 'Path']
BUILDING_TYPES = ['Tower', 'Heights', 'Residency', 'Plaza', 'Complex', 'Apartments']

def generate_address(area, city):
    """Generate a realistic Indian address"""
    building_num = random.randint(1, 500)
    street_num = random.randint(1, 50)
    street_type = random.choice(STREET_TYPES)
    building = random.choice(BUILDING_TYPES)
    
    address = f"{building_num}, {area} {building}, {street_num}th {street_type}, {area}, {city}"
    return address

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula (in km)"""
    R = 6371  # Earth radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def generate_coordinates_nearby(base_lat, base_lon, max_distance_km=15):
    """Generate coordinates within a certain distance from base coordinates"""
    # Approximate: 1 degree latitude = 111 km, 1 degree longitude varies
    distance_km = random.uniform(0.5, max_distance_km)
    angle = random.uniform(0, 2 * math.pi)
    
    # Convert to degrees (rough approximation)
    delta_lat = (distance_km / 111) * math.cos(angle)
    delta_lon = (distance_km / (111 * math.cos(math.radians(base_lat)))) * math.sin(angle)
    
    new_lat = base_lat + delta_lat
    new_lon = base_lon + delta_lon
    
    return new_lat, new_lon

def calculate_road_distance(straight_distance):
    """
    Calculate road distance from straight-line distance
    Road distance is typically 1.3-1.5x the straight-line distance in cities
    """
    multiplier = random.uniform(1.25, 1.45)
    return straight_distance * multiplier

# Generate dataset
n_samples = 10000
data = []

print("Generating enhanced dataset with full addresses...")

for i in range(n_samples):
    # Select city
    city = random.choice(list(CITIES.keys()))
    city_data = CITIES[city]
    city_lat, city_lon = city_data['coords']
    
    # Select restaurant
    restaurant_name = random.choice(list(RESTAURANTS.keys()))
    restaurant_data = RESTAURANTS[restaurant_name]
    
    # Restaurant location (random area in city)
    restaurant_area = random.choice(city_data['areas'])
    rest_lat, rest_lon = generate_coordinates_nearby(city_lat, city_lon, max_distance_km=10)
    restaurant_address = generate_address(restaurant_area, city)
    
    # Delivery location (different area)
    delivery_areas = [a for a in city_data['areas'] if a != restaurant_area]
    delivery_area = random.choice(delivery_areas) if delivery_areas else restaurant_area
    del_lat, del_lon = generate_coordinates_nearby(city_lat, city_lon, max_distance_km=12)
    delivery_address = generate_address(delivery_area, city)
    
    # Calculate actual straight-line distance
    straight_distance = haversine_distance(rest_lat, rest_lon, del_lat, del_lon)
    
    # Calculate road distance (realistic)
    road_distance = calculate_road_distance(straight_distance)
    road_distance = round(min(road_distance, 15), 2)  # Cap at 15km
    
    # Time features
    order_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 300))
    hour = random.randint(6, 23)
    is_weekend = 1 if order_date.weekday() >= 5 else 0
    
    # Meal type
    if 6 <= hour < 11:
        meal_type = 'Breakfast'
    elif 11 <= hour < 16:
        meal_type = 'Lunch'
    elif 16 <= hour < 19:
        meal_type = 'Snacks'
    else:
        meal_type = 'Dinner'
    
    # Order details
    num_items = random.randint(1, 6)
    order_value = random.randint(150, 1500)
    
    # Weather and traffic
    weather = random.choice(['Clear', 'Cloudy', 'Hot', 'Rain', 'Heavy Rain'])
    
    # Traffic based on time
    if hour in [12, 13, 19, 20, 21] or is_weekend:
        traffic = random.choices(['Low', 'Medium', 'High', 'Very High'], 
                                weights=[0.1, 0.2, 0.4, 0.3])[0]
    else:
        traffic = random.choices(['Low', 'Medium', 'High', 'Very High'], 
                                weights=[0.4, 0.4, 0.15, 0.05])[0]
    
    # Preparation time
    prep_min, prep_max = restaurant_data['prep_time']
    prep_time = random.randint(prep_min, prep_max) + (num_items * random.randint(1, 2))
    
    # Partner experience
    partner_experience = random.randint(1, 48)
    
    # Calculate delivery time
    base_time = road_distance * random.uniform(3, 5)
    
    traffic_multiplier = {'Low': 1.0, 'Medium': 1.2, 'High': 1.5, 'Very High': 1.8}
    weather_multiplier = {'Clear': 1.0, 'Cloudy': 1.05, 'Hot': 1.1, 'Rain': 1.3, 'Heavy Rain': 1.6}
    
    base_time *= traffic_multiplier[traffic]
    base_time *= weather_multiplier[weather]
    
    if hour in [13, 14, 20, 21]:
        base_time *= 1.15
    if is_weekend:
        base_time *= 1.1
    
    base_time *= (1 - (partner_experience / 500))
    
    total_time = prep_time + base_time
    total_time += random.uniform(-5, 5)
    total_time = max(15, round(total_time))
    
    data.append({
        'order_id': f'ORD{10000 + i}',
        'restaurant_name': restaurant_name,
        'restaurant_address': restaurant_address,
        'restaurant_area': restaurant_area,
        'restaurant_latitude': round(rest_lat, 6),
        'restaurant_longitude': round(rest_lon, 6),
        'delivery_address': delivery_address,
        'delivery_area': delivery_area,
        'delivery_latitude': round(del_lat, 6),
        'delivery_longitude': round(del_lon, 6),
        'city': city,
        'cuisine_type': restaurant_data['cuisine'],
        'straight_line_distance_km': round(straight_distance, 2),
        'road_distance_km': road_distance,
        'order_date': order_date.strftime('%Y-%m-%d'),
        'order_hour': hour,
        'day_type': 'Weekend' if is_weekend else 'Weekday',
        'meal_type': meal_type,
        'order_value_inr': order_value,
        'num_items': num_items,
        'weather_condition': weather,
        'traffic_level': traffic,
        'preparation_time_min': prep_time,
        'restaurant_rating': restaurant_data['rating'],
        'delivery_partner_experience_months': partner_experience,
        'actual_delivery_time_min': total_time
    })
    
    if (i + 1) % 1000 == 0:
        print(f"Generated {i + 1}/{n_samples} samples...")

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('indian_food_delivery_enhanced.csv', index=False)

print("\n✓ Enhanced dataset generated successfully!")
print(f"\nDataset Shape: {df.shape}")
print(f"\nFirst few rows:")
print(df.head())
print(f"\nColumn names:")
print(df.columns.tolist())
print(f"\nStatistics:")
print(df[['straight_line_distance_km', 'road_distance_km', 'actual_delivery_time_min']].describe())
print(f"\nSample address:")
print(f"Restaurant: {df.iloc[0]['restaurant_address']}")
print(f"Delivery: {df.iloc[0]['delivery_address']}")