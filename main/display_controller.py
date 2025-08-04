from machine import SPI, Pin
from ST7796 import LCD_35_ST7796, SPI_W_SPEED, Delay_Ms
from Font_6x12_EN import Font_6x12_EN
import time

#pin define
LCD_RS = 2
LCD_CS = 15
LCD_SCK = 14
LCD_SDA = 13
LCD_SDO = 12
LCD_BL = 27

# Enhanced color palette
BLACK = 0x0000
WHITE = 0xFFFF
BLUE = 0x001F
GREEN = 0x07E0
RED = 0xF800
YELLOW = 0xFFE0
CYAN = 0x07FF
MAGENTA = 0xF81F
GRAY = 0x8410
DARK_GRAY = 0x4208
LIGHT_BLUE = 0x3D9F
ORANGE = 0xFD20
LIGHT_GRAY = 0xC618
DARK_GREEN = 0x0320
PURPLE = 0x8010

spi = SPI(1,baudrate=SPI_W_SPEED,sck=Pin(LCD_SCK),mosi=Pin(LCD_SDA),miso=Pin(LCD_SDO))
mylcd = LCD_35_ST7796(spi, LCD_CS, LCD_RS, LCD_BL)
mylcd.LCD_Set_Rotate(1)

def draw_header():
    """Draw a professional header"""
    # Header background with gradient effect
    mylcd.Fill_Rect(0, 0, mylcd.lcd_width, 35, DARK_GRAY)
    mylcd.Fill_Rect(0, 0, mylcd.lcd_width, 2, BLUE)
    
    # Title with plane icon
    mylcd.Show_String(10, 10, "FLIGHT RADAR", Font_6x12_EN, WHITE)
    draw_plane_icon(130, 16, WHITE)
    
    # Status indicator
    mylcd.Show_String(mylcd.lcd_width - 50, 10, "LIVE", Font_6x12_EN, GREEN)
    mylcd.Fill_Circle(mylcd.lcd_width - 60, 16, 3, GREEN)
    
    # Bottom border
    mylcd.Draw_Hline(0, 35, mylcd.lcd_width, LIGHT_GRAY)

def draw_plane_icon(x, y, color=WHITE):
    """Draw a plane icon"""
    # Main fuselage
    mylcd.Draw_Hline(x-8, y, 16, color)
    # Wings
    mylcd.Draw_Hline(x-10, y-1, 20, color)
    mylcd.Draw_Hline(x-6, y+1, 12, color)
    # Tail
    mylcd.Draw_Point(x+8, y-2, color)
    mylcd.Draw_Point(x+8, y+2, color)
    mylcd.Draw_Point(x+7, y-1, color)
    mylcd.Draw_Point(x+7, y+1, color)

def get_altitude_color(altitude):
    """Return color based on altitude"""
    if altitude < 1000:
        return RED
    elif altitude < 3000:
        return ORANGE
    elif altitude < 8000:
        return YELLOW
    elif altitude < 15000:
        return GREEN
    else:
        return CYAN

def get_distance_color(distance):
    """Return color based on distance"""
    if distance < 5:
        return RED
    elif distance < 15:
        return ORANGE
    elif distance < 30:
        return YELLOW
    else:
        return GREEN

def draw_info_box(x, y, width, height, title, value, color=WHITE):
    """Draw a styled information box"""
    # Box outline
    mylcd.Draw_Rect(x, y, width, height, GRAY)
    # Title background
    mylcd.Fill_Rect(x+1, y+1, width-2, 12, DARK_GRAY)
    # Title text
    mylcd.Show_String(x+3, y+3, title, Font_6x12_EN, LIGHT_GRAY)
    # Value text
    mylcd.Show_String(x+3, y+15, value, Font_6x12_EN, color)

def draw_bearing_indicator(x, y, bearing):
    """Draw a compass bearing indicator"""
    # Outer circle
    mylcd.Draw_Circle(x, y, 12, GRAY)
    # Inner dot
    mylcd.Fill_Circle(x, y, 2, WHITE)
    
    # Calculate bearing line
    import math
    rad = math.radians(bearing - 90)  # -90 so 0° points north
    end_x = int(x + 10 * math.cos(rad))
    end_y = int(y + 10 * math.sin(rad))
    
    # Bearing line
    mylcd.Draw_line(x, y, end_x, end_y, YELLOW)
    mylcd.Fill_Circle(end_x, end_y, 1, YELLOW)
    
    # North indicator
    mylcd.Show_String(x-3, y-20, "N", Font_6x12_EN, WHITE)

def draw_flight_card(plane, y_pos, is_closest=False):
    """Draw an enhanced flight information card"""
    card_height = 55
    card_width = mylcd.lcd_width - 20
    x = 10
    
    # Card background - highlight closest plane
    bg_color = DARK_GREEN if is_closest else BLACK
    border_color = GREEN if is_closest else GRAY
    
    mylcd.Fill_Rect(x, y_pos, card_width, card_height, bg_color)
    mylcd.Draw_Rect(x, y_pos, card_width, card_height, border_color)
    
    # Callsign with plane icon
    callsign = plane.get('callsign', '[NO CALL]')[:10]
    draw_plane_icon(x + 15, y_pos + 8, WHITE)
    mylcd.Show_String(x + 30, y_pos + 5, callsign, Font_6x12_EN, WHITE)
    
    # Distance badge (top right)
    dist_color = get_distance_color(plane['distance_km'])
    dist_text = f"{plane['distance_km']}km"
    mylcd.Show_String(x + card_width - 50, y_pos + 5, dist_text, Font_6x12_EN, dist_color)
    
    # Altitude with color coding
    alt_color = get_altitude_color(plane['alt'])
    alt_text = f"ALT: {plane['alt']:,}m"
    mylcd.Show_String(x + 5, y_pos + 20, alt_text, Font_6x12_EN, alt_color)
    
    # Country origin
    country = plane.get('origin', 'Unknown')[:12]
    mylcd.Show_String(x + 5, y_pos + 35, f"FROM: {country}", Font_6x12_EN, LIGHT_GRAY)
    
    # Bearing with mini compass
    bearing_text = f"{plane['bearing']}°"
    mylcd.Show_String(x + card_width - 80, y_pos + 25, bearing_text, Font_6x12_EN, WHITE)
    draw_bearing_indicator(x + card_width - 25, y_pos + 35, plane['bearing'])

def draw_no_planes_screen():
    """Draw screen when no planes are visible"""
    mylcd.LCD_Clear(BLACK)
    draw_header()
    
    # Center message
    center_y = mylcd.lcd_height // 2 - 30
    
    # Large plane icon
    draw_plane_icon(mylcd.lcd_width // 2, center_y - 20, GRAY)
    
    # Message
    mylcd.Show_String(80, center_y, "No aircraft visible", Font_6x12_EN, GRAY)
    mylcd.Show_String(85, center_y + 15, "in viewing area", Font_6x12_EN, GRAY)
    
    # Search parameters info
    mylcd.Show_String(50, center_y + 40, "Scanning nearby airspace...", Font_6x12_EN, DARK_GRAY)

def draw_footer(plane_count, last_update_time=None):
    """Draw footer with status information"""
    footer_y = mylcd.lcd_height - 25
    
    # Footer background
    mylcd.Fill_Rect(0, footer_y, mylcd.lcd_width, 25, DARK_GRAY)
    mylcd.Draw_Hline(0, footer_y, mylcd.lcd_width, LIGHT_GRAY)
    
    # Plane count
    count_text = f"Aircraft: {plane_count}"
    mylcd.Show_String(10, footer_y + 8, count_text, Font_6x12_EN, WHITE)
    
    # Update indicator
    mylcd.Show_String(mylcd.lcd_width - 70, footer_y + 8, "AUTO", Font_6x12_EN, GREEN)
    # Blinking dot for activity
    mylcd.Fill_Circle(mylcd.lcd_width - 20, footer_y + 12, 2, GREEN)

def show_planes(planes):
    """Main display function with enhanced UI"""
    mylcd.LCD_Clear(BLACK)
    
    # Draw header
    draw_header()
    
    if not planes:
        draw_no_planes_screen()
        return
    
    # Status bar
    status_y = 40
    mylcd.Show_String(10, status_y, f"Tracking {len(planes)} aircraft", Font_6x12_EN, GREEN)
    
    if len(planes) > 0:
        closest_dist = planes[0]['distance_km']
        mylcd.Show_String(200, status_y, f"Closest: {closest_dist}km", Font_6x12_EN, YELLOW)
    
    # Calculate how many planes can fit
    available_height = mylcd.lcd_height - 95  # Account for header, status, footer
    card_height = 55
    card_spacing = 5
    max_planes = available_height // (card_height + card_spacing)
    
    # Display planes
    start_y = 60
    planes_to_show = min(len(planes), max_planes)
    
    for i in range(planes_to_show):
        plane = planes[i]
        card_y = start_y + i * (card_height + card_spacing)
        is_closest = (i == 0)  # Highlight the closest plane
        draw_flight_card(plane, card_y, is_closest)
    
    # Show remaining count if there are more planes
    if len(planes) > planes_to_show:
        remaining = len(planes) - planes_to_show
        mylcd.Show_String(10, mylcd.lcd_height - 45, 
                         f"+ {remaining} more aircraft", Font_6x12_EN, ORANGE)
    
    # Draw footer
    draw_footer(len(planes))