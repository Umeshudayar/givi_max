"""
Distance and Route Calculator using OpenStreetMap (OSM) data
No Google API required - Uses geopy and OSMnx
"""

import math
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests
import time

class DistanceCalculator:
    def __init__(self):
        # Initialize geocoder (free, no API key needed)
        self.geocoder = Nominatim(user_agent="food_delivery_app")
        
    def get_coordinates_from_address(self, address):
        """
        Convert address to latitude/longitude coordinates
        Uses OpenStreetMap Nominatim (free, no API key)
        """
        try:
            location = self.geocoder.geocode(address, timeout=10)
            if location:
                return {
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'formatted_address': location.address
                }
            else:
                return None
        except Exception as e:
            print(f"Error geocoding address: {e}")
            return None
    
    def calculate_straight_distance(self, coord1, coord2):
        """
        Calculate straight-line distance using Haversine formula
        coord1, coord2 = (latitude, longitude)
        Returns distance in kilometers
        """
        return geodesic(coord1, coord2).kilometers
    
    def calculate_road_distance_osrm(self, coord1, coord2):
        """
        Calculate road distance using OSRM (Open Source Routing Machine)
        Free routing service, no API key required
        Returns distance in km and duration in minutes
        """
        try:
            lat1, lon1 = coord1
            lat2, lon2 = coord2
            
            # OSRM API endpoint (free public instance)
            url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}"
            params = {
                'overview': 'full',
                'geometries': 'geojson',
                'steps': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['code'] == 'Ok':
                    route = data['routes'][0]
                    distance_km = route['distance'] / 1000  # Convert meters to km
                    duration_min = route['duration'] / 60   # Convert seconds to minutes
                    
                    return {
                        'distance_km': round(distance_km, 2),
                        'duration_min': round(duration_min, 1),
                        'geometry': route['geometry'],  # Route coordinates
                        'steps': self._extract_steps(route.get('legs', []))
                    }
            
            return None
            
        except Exception as e:
            print(f"Error calculating road distance: {e}")
            return None
    
    def _extract_steps(self, legs):
        """Extract turn-by-turn directions"""
        steps = []
        for leg in legs:
            for step in leg.get('steps', []):
                steps.append({
                    'instruction': step.get('maneuver', {}).get('type', 'continue'),
                    'distance': round(step['distance'] / 1000, 2),
                    'duration': round(step['duration'] / 60, 1)
                })
        return steps
    
    def estimate_road_distance(self, straight_distance):
        """
        Fallback: Estimate road distance from straight-line distance
        Use when OSRM is unavailable
        """
        # Urban areas: road distance is typically 1.3-1.5x straight distance
        multiplier = 1.35
        return round(straight_distance * multiplier, 2)
    
    def get_delivery_info(self, restaurant_address, delivery_address):
        """
        Complete function to get all delivery information
        """
        print(f"Getting coordinates for restaurant: {restaurant_address}")
        rest_coords = self.get_coordinates_from_address(restaurant_address)
        
        if not rest_coords:
            return {'error': 'Could not geocode restaurant address'}
        
        print(f"Getting coordinates for delivery location: {delivery_address}")
        del_coords = self.get_coordinates_from_address(delivery_address)
        
        if not del_coords:
            return {'error': 'Could not geocode delivery address'}
        
        # Calculate straight-line distance
        straight_dist = self.calculate_straight_distance(
            (rest_coords['latitude'], rest_coords['longitude']),
            (del_coords['latitude'], del_coords['longitude'])
        )
        
        # Try to get road distance from OSRM
        print("Calculating road distance...")
        route_info = self.calculate_road_distance_osrm(
            (rest_coords['latitude'], rest_coords['longitude']),
            (del_coords['latitude'], del_coords['longitude'])
        )
        
        if route_info:
            road_dist = route_info['distance_km']
            estimated_time = route_info['duration_min']
            geometry = route_info['geometry']
            steps = route_info['steps']
        else:
            # Fallback estimation
            road_dist = self.estimate_road_distance(straight_dist)
            estimated_time = road_dist * 4  # Rough estimate: 4 min per km
            geometry = None
            steps = None
        
        return {
            'restaurant': {
                'address': restaurant_address,
                'latitude': rest_coords['latitude'],
                'longitude': rest_coords['longitude'],
                'formatted_address': rest_coords['formatted_address']
            },
            'delivery': {
                'address': delivery_address,
                'latitude': del_coords['latitude'],
                'longitude': del_coords['longitude'],
                'formatted_address': del_coords['formatted_address']
            },
            'distance': {
                'straight_line_km': round(straight_dist, 2),
                'road_distance_km': road_dist,
                'estimated_time_min': round(estimated_time, 1)
            },
            'route': {
                'geometry': geometry,
                'steps': steps
            }
        }


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    calculator = DistanceCalculator()
    
    # Example 1: Calculate distance between two addresses
    print("="*60)
    print("Example 1: Full address to address calculation")
    print("="*60)
    
    restaurant_addr = "Koramangala, Bangalore, Karnataka, India"
    delivery_addr = "Indiranagar, Bangalore, Karnataka, India"
    
    result = calculator.get_delivery_info(restaurant_addr, delivery_addr)
    
    if 'error' not in result:
        print(f"\nRestaurant: {result['restaurant']['formatted_address']}")
        print(f"Delivery: {result['delivery']['formatted_address']}")
        print(f"\nStraight-line distance: {result['distance']['straight_line_km']} km")
        print(f"Road distance: {result['distance']['road_distance_km']} km")
        print(f"Estimated travel time: {result['distance']['estimated_time_min']} minutes")
        
        if result['route']['steps']:
            print(f"\nRoute has {len(result['route']['steps'])} steps")
    else:
        print(f"Error: {result['error']}")
    
    # Example 2: Quick distance calculation with coordinates
    print("\n" + "="*60)
    print("Example 2: Direct coordinate calculation")
    print("="*60)
    
    coord1 = (19.0760, 72.8777)  # Mumbai
    coord2 = (19.1136, 72.8697)  # Andheri
    
    straight = calculator.calculate_straight_distance(coord1, coord2)
    print(f"\nStraight-line distance: {straight:.2f} km")
    
    route = calculator.calculate_road_distance_osrm(coord1, coord2)
    if route:
        print(f"Road distance: {route['distance_km']} km")
        print(f"Estimated time: {route['duration_min']} minutes")
    
    # Example 3: Batch processing
    print("\n" + "="*60)
    print("Example 3: Processing multiple addresses")
    print("="*60)
    
    addresses = [
        ("Bandra West, Mumbai", "Andheri East, Mumbai"),
        ("Connaught Place, Delhi", "Dwarka, Delhi"),
    ]
    
    for rest_addr, del_addr in addresses:
        print(f"\n{rest_addr} → {del_addr}")
        result = calculator.get_delivery_info(rest_addr, del_addr)
        if 'error' not in result:
            print(f"  Distance: {result['distance']['road_distance_km']} km")
            print(f"  Time: {result['distance']['estimated_time_min']} min")
        time.sleep(1)  # Be nice to free API