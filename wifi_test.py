import network
import time

def scan_networks():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print("Scanning for Wi-Fi networks...")
    networks = wlan.scan()
    
    if networks:
        print("Found the following networks:")
        for ssid, bssid, channgel, rssi, authmode, hidden in networks:
            print(f" SSID: {ssid.decode('utf-8')}, RSSI: {rssi} dBm")
    else:
        print("No networks found.")
        
    wlan.active(False)

if __name__ == "__main__":
    scan_networks()