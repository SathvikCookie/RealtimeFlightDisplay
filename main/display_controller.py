from machine import SPI, Pin
from ST7796 import LCD_35_ST7796, SPI_W_SPEED, Delay_Ms
from Font_6x12_EN import Font_6x12_EN
import time
import math

#pin define
LCD_RS = 2
LCD_CS = 15
LCD_SCK = 14
LCD_SDA = 13
LCD_SDO = 12
LCD_BL = 27

# Cyberpunk Purple Color Palette
BLACK = 0x0000
WHITE = 0xFFFF
DEEP_BLACK = 0x0820          # Almost black with hint of purple
DARK_PURPLE = 0x2104         # Deep purple background
MEDIUM_PURPLE = 0x4A49       # Medium purple for panels
BRIGHT_PURPLE = 0x8C71       # Bright purple accents
NEON_PURPLE = 0xA254         # Electric purple
NEON_PINK = 0xF81F           # Hot pink/magenta
NEON_CYAN = 0x07FF           # Electric cyan
NEON_GREEN = 0x07E0          # Matrix green
ELECTRIC_BLUE = 0x1C9F       # Electric blue
GRID_PURPLE = 0x3186         # Grid line purple
TERMINAL_GREEN = 0x0400      # Dark terminal green
AMBER = 0xFD00               # Retro amber
ORANGE_RED = 0xFA00          # Warning orange-red
GRAY_BLUE = 0x528A           # Muted blue-gray
SCAN_LINE = 0x18E3           # Scanline effect color

spi = SPI(1,baudrate=SPI_W_SPEED,sck=Pin(LCD_SCK),mosi=Pin(LCD_SDA),miso=Pin(LCD_SDO))
mylcd = LCD_35_ST7796(spi, LCD_CS, LCD_RS, LCD_BL)
mylcd.LCD_Set_Rotate(1)

# Global state tracking
display_initialized = False
last_plane_count = -1
content_area_y = 70
content_area_height = 0

def draw_scanlines():
    """Draw subtle scanlines across the entire screen for retro CRT effect"""
    for y in range(0, mylcd.lcd_height, 4):
        mylcd.Draw_Hline(0, y, mylcd.lcd_width, SCAN_LINE)

def draw_grid_pattern(x, y, width, height):
    """Draw a cyberpunk grid pattern"""
    # Vertical grid lines
    for i in range(x, x + width, 20):
        mylcd.Draw_Vline(i, y, height, GRID_PURPLE)
    
    # Horizontal grid lines
    for i in range(y, y + height, 15):
        mylcd.Draw_Hline(x, i, width, GRID_PURPLE)

def draw_cyberpunk_border(x, y, width, height, color=NEON_PURPLE):
    """Draw a cyberpunk-style border with corner details"""
    # Main rectangle
    mylcd.Draw_Rect(x, y, width, height, color)
    
    # Corner decorations
    corner_size = 8
    # Top-left
    mylcd.Draw_Hline(x-2, y-2, corner_size, color)
    mylcd.Draw_Vline(x-2, y-2, corner_size, color)
    
    # Top-right
    mylcd.Draw_Hline(x + width - corner_size + 2, y-2, corner_size, color)
    mylcd.Draw_Vline(x + width + 1, y-2, corner_size, color)
    
    # Bottom-left
    mylcd.Draw_Hline(x-2, y + height + 1, corner_size, color)
    mylcd.Draw_Vline(x-2, y + height - corner_size + 2, corner_size, color)
    
    # Bottom-right
    mylcd.Draw_Hline(x + width - corner_size + 2, y + height + 1, corner_size, color)
    mylcd.Draw_Vline(x + width + 1, y + height - corner_size + 2, corner_size, color)

def initialize_static_display():
    """Draw all static elements once"""
    global display_initialized, content_area_height
    
    mylcd.LCD_Clear(DEEP_BLACK)
    draw_scanlines()
    
    # Draw header
    mylcd.Fill_Rect(0, 0, mylcd.lcd_width, 40, DEEP_BLACK)
    mylcd.Fill_Rect(0, 0, mylcd.lcd_width, 3, NEON_PURPLE)
    mylcd.Fill_Rect(0, 3, mylcd.lcd_width, 1, NEON_PINK)
    
    # Grid pattern in header
    draw_grid_pattern(0, 5, mylcd.lcd_width, 30)
    
    # Title with appropriate styling
    mylcd.Show_String(10, 10, "FLIGHT RADAR v2.1", Font_6x12_EN, NEON_CYAN)
    mylcd.Show_String(10, 25, " AIRSPACE MONITOR", Font_6x12_EN, TERMINAL_GREEN)
    
    # Status indicators
    draw_status_led(mylcd.lcd_width - 80, 12, NEON_GREEN, "ONLINE")
    draw_status_led(mylcd.lcd_width - 80, 25, NEON_PINK, "TRACK")
    
    # Header border
    mylcd.Draw_Hline(0, 40, mylcd.lcd_width, NEON_PURPLE)
    mylcd.Draw_Hline(0, 41, mylcd.lcd_width, BRIGHT_PURPLE)
    
    # Info bar background (static)
    info_y = 45
    mylcd.Fill_Rect(0, info_y, mylcd.lcd_width, 20, MEDIUM_PURPLE)
    
    # Status bar background (static)
    status_height = 25
    status_y = mylcd.lcd_height - status_height
    mylcd.Fill_Rect(0, status_y, mylcd.lcd_width, status_height, DEEP_BLACK)
    mylcd.Draw_Hline(0, status_y, mylcd.lcd_width, NEON_PURPLE)
    mylcd.Draw_Hline(0, status_y + 1, mylcd.lcd_width, BRIGHT_PURPLE)
    
    # Static status bar text
    mylcd.Show_String(5, status_y + 8, "SYS:OK", Font_6x12_EN, NEON_GREEN)
    mylcd.Show_String(50, status_y + 8, "ADS-B", Font_6x12_EN, NEON_CYAN)
    mylcd.Show_String(110, status_y + 8, "REALTIME", Font_6x12_EN, AMBER)
    
    content_area_height = mylcd.lcd_height - 95
    display_initialized = True

def draw_status_led(x, y, color, text):
    """Draw a small status LED with text"""
    # LED with glow effect
    mylcd.Fill_Circle(x, y, 3, color)
    mylcd.Fill_Circle(x, y, 1, WHITE)
    mylcd.Draw_Circle(x, y, 4, color)
    
    # Status text
    mylcd.Show_String(x + 8, y - 6, text, Font_6x12_EN, color)

def draw_retro_plane_icon(x, y, color=NEON_CYAN, size=1):
    """Draw a pixelated retro plane icon"""
    s = size
    # Main body (more angular/pixelated)
    mylcd.Fill_Rect(x-6*s, y-1*s, 12*s, 2*s, color)
    mylcd.Fill_Rect(x-4*s, y-2*s, 8*s, 1*s, color)
    mylcd.Fill_Rect(x-4*s, y+1*s, 8*s, 1*s, color)
    
    # Wings (more geometric)
    mylcd.Fill_Rect(x-8*s, y-3*s, 16*s, 1*s, color)
    mylcd.Fill_Rect(x-2*s, y+2*s, 8*s, 1*s, color)
    
    # Tail (sharp angles)
    mylcd.Fill_Rect(x+6*s, y-4*s, 2*s, 2*s, color)
    mylcd.Fill_Rect(x+6*s, y+2*s, 2*s, 2*s, color)
    
    # Nose (pointed)
    mylcd.Fill_Rect(x-8*s, y, 2*s, 1*s, color)

def get_altitude_color_cyber(altitude):
    """Return cyberpunk colors based on altitude"""
    if altitude < 1000:
        return ORANGE_RED
    elif altitude < 3000:
        return AMBER
    elif altitude < 8000:
        return NEON_PINK
    elif altitude < 15000:
        return NEON_PURPLE
    else:
        return NEON_CYAN

def get_distance_color_cyber(distance):
    """Return cyberpunk colors based on distance"""
    if distance < 5:
        return NEON_GREEN
    elif distance < 15:
        return NEON_CYAN
    elif distance < 30:
        return NEON_PURPLE
    else:
        return GRAY_BLUE

def draw_radar_compass(x, y, bearing):
    """Draw a retro radar-style compass"""
    radius = 15
    
    # Clear the area first
    mylcd.Fill_Circle(x, y, radius + 2, DARK_PURPLE)
    
    # Outer circle with scan effect
    mylcd.Draw_Circle(x, y, radius, NEON_PURPLE)
    mylcd.Draw_Circle(x, y, radius-1, BRIGHT_PURPLE)
    
    # Grid lines (crosshairs)
    mylcd.Draw_Hline(x-radius, y, radius*2, GRID_PURPLE)
    mylcd.Draw_Vline(x, y-radius, radius*2, GRID_PURPLE)
    
    # Diagonal lines
    for i in range(-radius+2, radius-1):
        mylcd.Draw_Point(x+i, y+i, GRID_PURPLE)
        mylcd.Draw_Point(x+i, y-i, GRID_PURPLE)
    
    # Center dot
    mylcd.Fill_Circle(x, y, 2, NEON_GREEN)
    
    # Bearing indicator
    rad = math.radians(bearing - 90)
    end_x = int(x + (radius-3) * math.cos(rad))
    end_y = int(y + (radius-3) * math.sin(rad))
    
    mylcd.Draw_line(x, y, end_x, end_y, NEON_CYAN)
    mylcd.Fill_Circle(end_x, end_y, 2, NEON_CYAN)

def clear_content_area():
    """Clear only the content area for updates"""
    mylcd.Fill_Rect(10, content_area_y, mylcd.lcd_width - 20, content_area_height, DEEP_BLACK)

def update_info_bar(plane_count, closest_dist=None):
    """Update just the info bar text"""
    info_y = 45
    # Clear text area
    mylcd.Fill_Rect(5, info_y + 2, mylcd.lcd_width - 10, 16, MEDIUM_PURPLE)
    
    # Update plane count
    if plane_count < 10:
        count_text = "TRACKING:0" + str(plane_count) + "_AIRCRAFT"
    else:
        count_text = "TRACKING:" + str(plane_count) + "_AIRCRAFT"
    mylcd.Show_String(10, info_y + 5, count_text, Font_6x12_EN, NEON_GREEN)
    
    # Update closest distance
    if closest_dist is not None:
        closest_val = int(closest_dist)
        if closest_val < 10:
            nearest_text = "NEAREST:00" + str(closest_val) + "KM"
        elif closest_val < 100:
            nearest_text = "NEAREST:0" + str(closest_val) + "KM"
        else:
            nearest_text = "NEAREST:" + str(closest_val) + "KM"
        mylcd.Show_String(180, info_y + 5, nearest_text, Font_6x12_EN, NEON_PINK)

def update_status_activity():
    """Update just the activity indicator in status bar"""
    status_y = mylcd.lcd_height - 25
    # Clear activity area
    mylcd.Fill_Rect(mylcd.lcd_width - 70, status_y + 5, 65, 15, DEEP_BLACK)
    
    mylcd.Show_String(mylcd.lcd_width - 60, status_y + 8, "ACTIVE", Font_6x12_EN, NEON_PINK)
    # Blinking dot
    mylcd.Fill_Circle(mylcd.lcd_width - 10, status_y + 12, 3, NEON_GREEN)

def draw_data_panel(plane, y_pos, is_priority=False):
    """Draw a cyberpunk data panel for each aircraft"""
    panel_height = 60
    panel_width = mylcd.lcd_width - 20
    x = 10
    
    # Panel background
    if is_priority:
        mylcd.Fill_Rect(x-1, y_pos-1, panel_width+2, panel_height+2, NEON_PURPLE)
        mylcd.Fill_Rect(x, y_pos, panel_width, panel_height, DARK_PURPLE)
        draw_cyberpunk_border(x, y_pos, panel_width, panel_height, NEON_PINK)
    else:
        mylcd.Fill_Rect(x, y_pos, panel_width, panel_height, MEDIUM_PURPLE)
        draw_cyberpunk_border(x, y_pos, panel_width, panel_height, BRIGHT_PURPLE)
    
    # Grid pattern in background
    draw_grid_pattern(x+2, y_pos+2, panel_width-4, panel_height-4)
    
    # Aircraft icon
    icon_color = NEON_PINK if is_priority else NEON_CYAN
    draw_retro_plane_icon(x + 20, y_pos + 15, icon_color)
    
    # Callsign with terminal styling
    callsign = plane.get('callsign', '[UNKNOWN]')[:10]
    mylcd.Show_String(x + 35, y_pos + 8, "ID:" + callsign, Font_6x12_EN, NEON_CYAN)
    
    # Distance with digital readout style
    dist_color = get_distance_color_cyber(plane['distance_km'])
    dist_val = int(plane['distance_km'])
    if dist_val < 10:
        dist_text = "RNG:00" + str(dist_val) + "KM"
    elif dist_val < 100:
        dist_text = "RNG:0" + str(dist_val) + "KM"
    else:
        dist_text = "RNG:" + str(dist_val) + "KM"
    mylcd.Show_String(x + panel_width - 80, y_pos + 8, dist_text, Font_6x12_EN, dist_color)
    
    # Altitude with color coding
    alt_color = get_altitude_color_cyber(plane['alt'])
    alt_val = int(plane['alt'])
    alt_str = str(alt_val)
    while len(alt_str) < 5:
        alt_str = "0" + alt_str
    alt_text = "ALT:" + alt_str + "M"
    mylcd.Show_String(x + 5, y_pos + 25, alt_text, Font_6x12_EN, alt_color)
    
    # Origin with data format
    country = plane.get('origin', 'UNK')[:8]
    mylcd.Show_String(x + 5, y_pos + 40, "FROM:" + country, Font_6x12_EN, GRAY_BLUE)
    
    # Bearing with compass
    bearing_val = int(plane['bearing'])
    if bearing_val < 10:
        bearing_text = "HDG:00" + str(bearing_val)
    elif bearing_val < 100:
        bearing_text = "HDG:0" + str(bearing_val)
    else:
        bearing_text = "HDG:" + str(bearing_val)
    mylcd.Show_String(x + panel_width - 100, y_pos + 25, bearing_text, Font_6x12_EN, AMBER)
    draw_radar_compass(x + panel_width - 25, y_pos + 35, plane['bearing'])
    
    # Data stream effect (moving dots)
    for i in range(3):
        dot_x = x + 150 + i * 15
        mylcd.Fill_Circle(dot_x, y_pos + 45, 1, TERMINAL_GREEN)

def draw_no_signal_screen():
    """Draw screen when no aircraft detected - cyberpunk style"""
    if not display_initialized:
        initialize_static_display()
    
    clear_content_area()
    update_info_bar(0)
    
    # Large central display
    center_y = mylcd.lcd_height // 2 - 40
    
    # Radar sweep circle
    mylcd.Draw_Circle(mylcd.lcd_width // 2, center_y, 80, NEON_PURPLE)
    mylcd.Draw_Circle(mylcd.lcd_width // 2, center_y, 60, BRIGHT_PURPLE)
    mylcd.Draw_Circle(mylcd.lcd_width // 2, center_y, 40, GRID_PURPLE)
    mylcd.Draw_Circle(mylcd.lcd_width // 2, center_y, 20, GRID_PURPLE)
    
    # Crosshairs
    mylcd.Draw_Hline(mylcd.lcd_width // 2 - 80, center_y, 160, GRID_PURPLE)
    mylcd.Draw_Vline(mylcd.lcd_width // 2, center_y - 80, 160, GRID_PURPLE)
    
    # Center aircraft icon
    draw_retro_plane_icon(mylcd.lcd_width // 2, center_y, GRAY_BLUE, 2)
    
    # Status messages
    mylcd.Show_String(60, center_y + 100, ">>> NO AIRCRAFT DETECTED <<<", Font_6x12_EN, ORANGE_RED)
    mylcd.Show_String(80, center_y + 115, "SCANNING AIRSPACE...", Font_6x12_EN, TERMINAL_GREEN)
    mylcd.Show_String(100, center_y + 130, "STANDBY MODE", Font_6x12_EN, NEON_CYAN)
    
    update_status_activity()

def show_planes(planes):
    """Main display function with optimized updates"""
    global last_plane_count
    
    # Initialize static elements if needed
    if not display_initialized:
        initialize_static_display()
    
    if not planes:
        draw_no_signal_screen()
        last_plane_count = 0
        return
    
    # Only clear and redraw if plane count changed significantly
    current_count = len(planes)
    if abs(current_count - last_plane_count) > 0:
        clear_content_area()
        last_plane_count = current_count
    
    # Update info bar
    closest_dist = planes[0]['distance_km'] if planes else None
    update_info_bar(current_count, closest_dist)
    
    # Calculate display area
    panel_height = 60
    panel_spacing = 5
    max_planes = content_area_height // (panel_height + panel_spacing)
    
    # Display aircraft panels
    planes_to_show = min(len(planes), max_planes)
    
    for i in range(planes_to_show):
        plane = planes[i]
        panel_y = content_area_y + i * (panel_height + panel_spacing)
        is_priority = (i == 0)  # Highlight closest target
        draw_data_panel(plane, panel_y, is_priority)
    
    # Overflow indicator
    if len(planes) > planes_to_show:
        remaining = len(planes) - planes_to_show
        overflow_y = mylcd.lcd_height - 50
        mylcd.Fill_Rect(5, overflow_y, mylcd.lcd_width - 10, 15, DARK_PURPLE)
        if remaining < 10:
            remaining_text = ">>> 0" + str(remaining) + " MORE AIRCRAFT IN RANGE <<<"
        else:
            remaining_text = ">>> " + str(remaining) + " MORE AIRCRAFT IN RANGE <<<"
        mylcd.Show_String(10, overflow_y + 3, remaining_text, Font_6x12_EN, AMBER)
    
    # Update activity indicator
    update_status_activity()

# Function to force full redraw (call this occasionally or on errors)
def force_refresh():
    """Force a complete display refresh"""
    global display_initialized
    display_initialized = False