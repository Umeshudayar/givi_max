import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Indian cities and their popular cloud kitchens
cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Pune', 'Chennai', 'Kolkata']
restaurants = [
    'Biryani Blues', 'Faasos', 'Behrouz Biryani', 'Oven Story Pizza',
    'The Bowl Company', 'Lunch Box', 'Mandarin Oak', 'Firangi Bake',
    'Slay Coffee', 'EatFit', 'WarmOven', 'Box8', 'Freshmenu'
]

cuisines = ['North Indian', 'South Indian', 'Chinese', 'Italian', 'Biryani', 'Fast Food', 'Healthy']
meal_types = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
weather_conditions = ['Clear', 'Rain', 'Heavy Rain', 'Cloudy', 'Hot']
day_types = ['Weekday', 'Weekend']
traffic_levels = ['Low', 'Medium', 'High', 'Very High']

# Generate 10000 samples
n_samples = 10000
data = []

for i in range(n_samples):
    # Basic info
    city = random.choice(cities)
    restaurant = random.choice(restaurants)
    cuisine = random.choice(cuisines)
    
    # Time features
    order_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 300))
    hour = random.randint(6, 23)
    is_weekend = 1 if order_date.weekday() >= 5 else 0
    day_type = 'Weekend' if is_weekend else 'Weekday'
    
    # Determine meal type based on hour
    if 6 <= hour < 11:
        meal_type = 'Breakfast'
    elif 11 <= hour < 16:
        meal_type = 'Lunch'
    elif 16 <= hour < 19:
        meal_type = 'Snacks'
    else:
        meal_type = 'Dinner'
    
    # Distance (in km) - realistic Indian delivery ranges
    distance = round(np.random.gamma(2, 1.5), 2)  # Most deliveries are 2-5 km
    distance = min(distance, 15)  # Cap at 15km
    
    # Order value (in INR)
    order_value = random.randint(150, 1500)
    
    # Number of items
    num_items = random.randint(1, 6)
    
    # Weather
    weather = random.choice(weather_conditions)
    
    # Traffic based on time and day
    if hour in [12, 13, 19, 20, 21] or is_weekend:
        traffic = random.choices(traffic_levels, weights=[0.1, 0.2, 0.4, 0.3])[0]
    else:
        traffic = random.choices(traffic_levels, weights=[0.4, 0.4, 0.15, 0.05])[0]
    
    # Preparation time (minutes) - varies by cuisine and items
    base_prep_time = random.randint(8, 25)
    prep_time = base_prep_time + (num_items * random.randint(1, 3))
    
    # Restaurant rating
    restaurant_rating = round(random.uniform(3.5, 4.9), 1)
    
    # Delivery partner experience (months)
    partner_experience = random.randint(1, 48)
    
    # Calculate actual delivery time (target variable)
    # Base time from distance
    base_time = distance * random.uniform(3, 5)  # 3-5 min per km
    
    # Traffic impact
    traffic_multiplier = {'Low': 1.0, 'Medium': 1.2, 'High': 1.5, 'Very High': 1.8}
    base_time *= traffic_multiplier[traffic]
    
    # Weather impact
    weather_multiplier = {'Clear': 1.0, 'Cloudy': 1.05, 'Hot': 1.1, 'Rain': 1.3, 'Heavy Rain': 1.6}
    base_time *= weather_multiplier[weather]
    
    # Peak hour impact
    if hour in [13, 14, 20, 21]:
        base_time *= 1.15
    
    # Weekend impact
    if is_weekend:
        base_time *= 1.1
    
    # Partner experience reduces time
    base_time *= (1 - (partner_experience / 500))
    
    # Add preparation time
    total_time = prep_time + base_time
    
    # Add some randomness
    total_time += random.uniform(-5, 5)
    total_time = max(15, round(total_time))  # Minimum 15 minutes
    
    data.append({
        'restaurant_name': restaurant,
        'city': city,
        'cuisine_type': cuisine,
        'order_date': order_date.strftime('%Y-%m-%d'),
        'order_hour': hour,
        'day_type': day_type,
        'meal_type': meal_type,
        'distance_km': distance,
        'order_value_inr': order_value,
        'num_items': num_items,
        'weather_condition': weather,
        'traffic_level': traffic,
        'preparation_time_min': prep_time,
        'restaurant_rating': restaurant_rating,
        'delivery_partner_experience_months': partner_experience,
        'actual_delivery_time_min': total_time
    })

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('indian_food_delivery_data.csv', index=False)

print("Dataset Generated Successfully!")
print(f"\nDataset Shape: {df.shape}")
print(f"\nFirst few rows:")
print(df.head())
print(f"\nStatistics:")
print(df.describe())
print(f"\nDelivery Time Distribution:")
print(f"Mean: {df['actual_delivery_time_min'].mean():.2f} minutes")
print(f"Median: {df['actual_delivery_time_min'].median():.2f} minutes")
print(f"Min: {df['actual_delivery_time_min'].min():.2f} minutes")
print(f"Max: {df['actual_delivery_time_min'].max():.2f} minutes")