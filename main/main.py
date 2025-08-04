import time

from wifi_connect import connect_to_wifi
from flight_fetcher import get_visible_planes

connect_to_wifi()

while True:
    print("Checking visible planes...")
    planes = get_visible_planes()
    print("Found {} visible plane(s):".format(len(planes)))
    for p in planes:
        print("✈️ {} | Alt: {}m | Dist: {}km | Bearing: {}° | From: {}".format(
            p['callsign'] or '[no callsign]', p['alt'], p['distance_km'], p['bearing'], p['origin']
        ))
    time.sleep(10)