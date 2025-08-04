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

#color define
BLACK = 0x0000
WHITE = 0xFFFF

spi = SPI(1,baudrate=SPI_W_SPEED,sck=Pin(LCD_SCK),mosi=Pin(LCD_SDA),miso=Pin(LCD_SDO))
mylcd = LCD_35_ST7796(spi, LCD_CS, LCD_RS, LCD_BL)
mylcd.LCD_Set_Rotate(1)

def show_planes(planes):
    mylcd.LCD_Clear(BLACK)
    
    y = 15
    
    if planes:
        for p in planes:
            mylcd.Show_String(15, y, "{} | Alt: {}m | Dist: {}km | Bearing: {}° | From: {}".format(
                    p['callsign'] or '[no callsign]', p['alt'], p['distance_km'], p['bearing'], p['origin']
                    ), Font_6x12_EN, WHITE)
            y = y + 16
    else:
        mylcd.Show_String(20, y, "No planes currently visible", Font_6x12_EN, WHITE)
        