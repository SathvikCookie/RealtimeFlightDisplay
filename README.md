# ✈️ Airport Departure Display (Python Prototype)

This is a Python prototype for an ESP32-based live flight tracking board. It fetches real-time flight data for a given location, and performs calculations on the bearing, distance, and more for to determine which flights are visible from your selected window. Fetched and filtered data is displayed on a ST7796S board, run by an ESP32.

---

## 🔍 What It Does

- Connects to the OpenSky Network API
- Fetches data for airlines within given latitude and longitude coordinates
- Outputs formatted flight information to the terminal
- Serves as a data pipeline prototype before hardware implementation

---

## 🧰 Requirements

Install Python dependencies:

```bash
pip install requests
```

---

## To Be Implemented

- Get additional flight metadata to display (destination, airline, etc.)
- Build display driver for LED screen
- Build ESP32 and ST7796S prototype
