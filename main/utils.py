import math

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