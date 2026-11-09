from geopy.distance import distance
from places.models import Places
from .geocoder_logic import fetch_coordinates


def count_restaurant_distance(client_lon, client_lat, rest_lat, rest_lon):
    result = []
    restaurants_place = Place.objects.all()
    for place in restaurants_place:
        restaurant_lat, restaurant_lon = place.lat, place.lon
        d = distance((client_lat, client_lon), (restaurant_lat, restaurant_lon)).km
        result.append({'restaurant': place.address, 'distance': d})
        
    result.sort(key=lambda x: x['distance'])
    return result
        
    
    