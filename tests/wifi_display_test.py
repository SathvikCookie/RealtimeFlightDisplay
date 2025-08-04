import network
import time
from machine import SPI, Pin
from ST7796 import LCD_35_ST7796, SPI_W_SPEED, Delay_Ms
from Font_6x12_EN import Font_6x12_EN

#pin define
LCD_RS = 2
LCD_CS = 15
#LCD_RST = 27  #connect to ESP32 reset pin
LCD_SCK = 14
LCD_SDA = 13
LCD_SDO = 12
LCD_BL = 27

#color_define
BLACK = 0x0000
WHITE = 0xFFFF

spi = SPI(1,baudrate=SPI_W_SPEED,sck=Pin(LCD_SCK),mosi=Pin(LCD_SDA),miso=Pin(LCD_SDO))
mylcd = LCD_35_ST7796(spi, LCD_CS, LCD_RS, LCD_BL)

# Get a list of the first 10 available WiFi networks
def get_networks():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print("Scanning for Wi-Fi networks...")
    networks = wlan.scan()
    wlan.active(False)
    
    return networks

# Get networks and print them
def print_networks():
    networks = get_networks()
    mylcd.LCD_Clear(WHITE)
    y = 20
    
    if networks:
        print("Found the following networks:")
        for ssid, bssid, channgel, rssi, authmode, hidden in networks:
            print(f" SSID: {ssid.decode('utf-8')}, RSSI: {rssi} dBm")
            mylcd.Show_String(20, y, f" SSID: {ssid.decode('utf-8')}, RSSI: {rssi} dBm", Font_6x12_EN, BLACK)
            y = y + 16
    else:
        print("No networks found.")

# Main method
if __name__=='__main__':
    print_networks()