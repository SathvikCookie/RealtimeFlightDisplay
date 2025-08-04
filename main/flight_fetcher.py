import urequests as requests
import math
import time
from config import USER_LAT, USER_LON, DELTA, WINDOW_DIR, FOV_DEG, MAX_RADIUS_KM, MAX_ALT_M
from utils import haversine_distance, calculate_bearing, is_within_view

def get_visible_planes():
    lamin = USER_LAT - DELTA
    lamax = USER_LAT + DELTA
    lomin = USER_LON - DELTA
    lomax = USER_LON + DELTA
    url = "https://opensky-network.org/api/states/all?lamin={}&lomin={}&lamax={}&lomax={}".format(lamin, lomin, lamax, lomax)

    try:
        res = requests.get(url)
        if res.status_code != 200:
            print("Failed to get data, status:", res.status_code)
            return []
        data = res.json()
        res.close()  # Important to close response to free memory
    except Exception as e:
        print("Request error:", e)
        return []
    
    visible_planes = []
    states = data.get("states", [])
    print("Checking {} planes".format(len(states)))

    for plane in states:
        icao24 = plane[0]
        callsign = plane[1]
        origin_country = plane[2]
        lon, lat, alt = plane[5], plane[6], plane[7]

        if lat is None or lon is None or alt is None:
            continue

        distance = haversine_distance(USER_LAT, USER_LON, lat, lon)
        if distance > MAX_RADIUS_KM or alt > MAX_ALT_M:
            continue

        bearing = calculate_bearing(USER_LAT, USER_LON, lat, lon)
        if not is_within_view(bearing, WINDOW_DIR, FOV_DEG):
            continue

        visible_planes.append({
            "callsign": callsign,
            "icao24": icao24,
            "origin": origin_country,
            "lat": lat,
            "lon": lon,
            "alt": int(alt),
            "distance_km": round(distance, 1),
            "bearing": int(bearing)
        })
    
    visible_planes.sort(key=lambda item: item.get("distance_km", float('inf')))
    return visible_planes
