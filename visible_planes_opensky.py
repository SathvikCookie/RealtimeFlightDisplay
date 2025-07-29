import requests
import math
import time
from datetime import datetime

# === USER VARS ===
USER_LAT = 47.6205
USER_LON = -122.3493
DELTA = 0.2
WINDOW_DIR = 180
FOV_DEG = 60
MAX_RADIUS_KM = 30
MAX_ALT_M = 12000

# === HELPER FUNCTIONS ===
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

def calculate_bearing(lat1, lon1, lat2, lon2):
    # Returns bearing from point 1 to point 2 in degrees
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dlon)
    bearing = math.atan2(x, y)
    return (math.degrees(bearing) + 360) % 360

def is_within_view(bearing, window_dir, fov):
    half_fov = fov / 2
    lower = (window_dir - half_fov) % 360
    upper = (window_dir + half_fov) % 360
    if lower < upper:
        return lower <= bearing <= upper
    else:
        return bearing >= lower or bearing <= upper

# === MAIN FUNCTION ===
def get_visible_planes():
    lamin = USER_LAT - DELTA
    lamax = USER_LAT + DELTA
    lomin = USER_LON - DELTA
    lomax = USER_LON + DELTA
    url = f"https://opensky-network.org/api/states/all?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}"
    # url = "https://opensky-network.org/api/states/all"

    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print("Failed to get data", e)
        return []
    
    data = res.json()
    visible_planes = []

    print(f"Checking {len(data.get('states', []))} planes")

    for plane in data.get("states", []):
        icao24 = plane[0]
        callsign = plane[1]
        origin_country = plane[2]
        lon, lat, alt = plane[5], plane[6], plane[7]

        if not lat or not lon or not alt:
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
    
    return visible_planes

def get_flight_details():
    return []

# === RUN IT ===
if __name__ == "__main__":
    while True:
        time.sleep(10)
        print("Checking visible planes...")
        planes = get_visible_planes()
        print(f"Found {len(planes)} visible plane(s):\n")
        for p in planes:
            print(f"✈️ {p['callsign'] or '[no callsign]'} | Alt: {p['alt']}m | Dist: {p['distance_km']}km | Bearing: {p['bearing']}° | From: {p['origin']}")