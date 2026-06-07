import googlemaps
from app.core.config import GOOGLE_MAPS_API_KEY

gmaps = None
if GOOGLE_MAPS_API_KEY:
    try:
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    except Exception as e:
        print(f"Failed to initialize Google Maps backend client: {e}")

def get_real_world_distance(origin_lat, origin_lon, dest_lat, dest_lon):
    """
    Uses the Google Maps Distance Matrix API to calculate actual walking distance.
    Returns distance in meters. Returns None if API key missing or request fails.
    """
    if not gmaps:
        return None
        
    try:
        matrix = gmaps.distance_matrix(
            origins=(origin_lat, origin_lon),
            destinations=(dest_lat, dest_lon),
            mode="walking"
        )
        
        # Parse the JSON response
        if matrix['status'] == 'OK':
            element = matrix['rows'][0]['elements'][0]
            if element['status'] == 'OK':
                return element['distance']['value'] # in meters
                
        return None
    except Exception:
        return None
