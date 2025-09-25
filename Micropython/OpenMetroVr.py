import time
import network
import urequests
from machine import Pin, PWM
from neopixel import Neopixel
import random
from time import sleep, ticks_ms, ticks_diff
import ujson

# --- Configuration ---
ssid = 'YourSSID'      # Your Wi-Fi SSID
password = 'YourPassword'  # Your Wi-Fi password
lat = "52.629238" # Update for location
lon = "0.492520" # Update for location

# --- Calibrated Servo Positions ---
# Your custom values have been added here.
servospeed = 0.02
servo_offset = 0

CLEAR_DAY_POS = 22
CLEAR_NIGHT_POS = 2
PARTLY_CLOUDY_POS = 45
PARTLY_CLOUDY_NIGHT_POS = 165
OVERCAST_POS = 60
FOG_POS = 113
SLIGHT_RAIN_POS = 90
RAIN_SHOWERS_POS = 75
MODERATE_RAIN_POS = 95
HEAVY_RAIN_POS = 95          # NOTE: This value was missing, I've set it to 85.
RAIN_NIGHT_POS = 150
THUNDERSTORM_POS = 50
SNOW_POS = 135

# --- Neopixel Configuration ---
numpix = 10
pixels_pin = 28
pixels = Neopixel(numpix, 0, pixels_pin, "GRB")
day_brightness = 0.5
night_brightness = 0.2

# --- Weather Configuration ---
weather_check_interval = 5 * 60 * 1000  # 5 minutes
last_weather_check = 0
conditions = 0
night = False
last_condition = None
first_weather_check = True

# --- Weather Condition Mapping ---
WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Rime fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Dense drizzle", 61: "Slight rain", 63: "Rain", 65: "Heavy rain",
    80: "Slight showers", 81: "Showers", 82: "Violent showers", 95: "Thunderstorm", 96: "Thunderstorm + Hail",
    71: "Slight snow", 73: "Snow", 75: "Heavy snow", 85: "Slight snow showers", 86: "Heavy snow showers"
}

# Define lists for your categories
clear_sky = [0, 1]
partly_cloudy = [2]
overcast = [3]
fog = [45, 48]
slight_rain = [51, 61]
rain_showers = [80, 81, 82]
moderate_rain = [53, 63]
heavy_rain = [55, 65]
thunderstorm = [95, 96, 99]
snow = [71, 73, 75, 85, 86]
all_rain_types = slight_rain + rain_showers + moderate_rain + heavy_rain

# --- Initialization ---
servoPin = PWM(Pin(16))
servoPin.freq(50)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
current_servo_position = 90 # Start at a neutral position

# --- Helper Functions ---
def connect():
    if not wlan.isconnected():
        print("Attempting to connect to Wi-Fi...")
        wlan.connect(ssid, password)
        for _ in range(15):
            if wlan.isconnected():
                print("Connected to Wi-Fi.")
                return True
            sleep(1)
        print("Failed to connect to Wi-Fi.")
        return False
    return True

def get_conditions():
    global conditions, night, last_weather_check
    current_time_ms = ticks_ms()
    if last_weather_check == 0 or ticks_diff(current_time_ms, last_weather_check) >= weather_check_interval:
        print("Getting Data from Open-Meteo...")
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            response = urequests.get(url)
            data = response.json()
            response.close()
            current_weather_data = data["current_weather"]
            conditions = int(current_weather_data["weathercode"])
            night = current_weather_data["is_day"] == 0
            condition_text = WMO_CODES.get(conditions, "Unknown")
            print(f"Weather updated: {condition_text} ({conditions}), Night: {night}")
            last_weather_check = ticks_ms()
        except Exception as e:
            print(f"Failed to fetch weather data: {e}")

# --- Ambient Lighting Effects ---
def clear_day_effect(duration_ms, start_time):
    brightness = day_brightness
    while ticks_diff(ticks_ms(), start_time) < duration_ms:
        pixels.fill((int(249 * brightness), int(215 * brightness), int(28 * brightness)))
        pixels.show()
        sleep(1)

def clear_night_effect(duration_ms, start_time):
    brightness = night_brightness
    moon_color = (int(150 * brightness), int(150 * brightness), int(255 * brightness))
    while ticks_diff(ticks_ms(), start_time) < duration_ms:
        pixels.fill(moon_color)
        pixels.show()
        sleep(1.0)

def clouds_effect(duration_ms, start_time):
    brightness = night_brightness if night else day_brightness
    cloud_color = (int(30 * brightness), int(30 * brightness), int(30 * brightness))
    while ticks_diff(ticks_ms(), start_time) < duration_ms:
        pixels.fill(cloud_color)
        pixels.show()
        sleep(0.5)

def rain_effect(duration_ms, start_time, speed=0.7):
    brightness = night_brightness if night else day_brightness
    num_drops = 2
    raindrops = [{'position': random.randint(0, numpix - 1)} for _ in range(num_drops)]
    while ticks_diff(ticks_ms(), start_time) < duration_ms:
        pixels.fill((0, 0, 0))
        for drop in raindrops:
            drop['position'] = (drop['position'] + 1) % numpix
            pixels.set_pixel(drop['position'], (0, 0, int(128 * brightness)))
        pixels.show()
        sleep(speed)

def thunderstorm_effect(duration_ms, start_time):
    start = ticks_ms()
    while ticks_diff(ticks_ms(), start) < duration_ms:
        rain_effect(1000, ticks_ms(), speed=0.4)
        if random.randint(0, 10) > 8:
            pixels.fill((255, 255, 255))
            pixels.show()
            sleep(0.1)
            pixels.fill((0, 0, 0))
            pixels.show()

def fog_effect(duration_ms, start_time):
    brightness = night_brightness if night else 0.3
    fog_color = (int(80 * brightness), int(80 * brightness), int(80 * brightness))
    while ticks_diff(ticks_ms(), start_time) < duration_ms:
        pixels.fill(fog_color)
        pixels.show()
        sleep(1.0)

def snow_effect(duration_ms, start_time):
    brightness = night_brightness if night else day_brightness
    snow_color = (int(255*brightness), int(255*brightness), int(255*brightness))
    snowflakes = [{'position': random.randint(0, numpix - 1)} for _ in range(2)]
    while ticks_diff(ticks_ms(), start_time) < duration_ms:
        pixels.fill((0, 0, 0))
        for flake in snowflakes:
            flake['position'] = (flake['position'] + 1) % numpix
            pixels.set_pixel(flake['position'], snow_color)
        pixels.show()
        sleep(0.8)

# --- Core Logic ---
def move():
    global last_condition, first_weather_check
    animation_duration_ms = weather_check_interval
    if first_weather_check or last_condition != conditions:
        print(f"New weather condition detected. Updating display.")
        start_time = ticks_ms()
        
        target_pos = None
        effect_func = None
        effect_params = {}

        # --- NEW LOGIC: Determine position and effect based on condition and time of day ---
        if night:
            if conditions in clear_sky:
                target_pos = CLEAR_NIGHT_POS
                effect_func = clear_night_effect
            elif conditions in partly_cloudy:
                target_pos = PARTLY_CLOUDY_NIGHT_POS
                effect_func = clouds_effect
            elif conditions in all_rain_types:
                target_pos = RAIN_NIGHT_POS
                effect_func = rain_effect
        
        # If it's day, or no specific night position was found, use day positions
        if target_pos is None:
            if conditions in clear_sky:
                target_pos = CLEAR_DAY_POS
                effect_func = clear_day_effect
            elif conditions in partly_cloudy:
                target_pos = PARTLY_CLOUDY_POS
                effect_func = clouds_effect
            elif conditions in overcast:
                target_pos = OVERCAST_POS
                effect_func = clouds_effect
            elif conditions in fog:
                target_pos = FOG_POS
                effect_func = fog_effect
            elif conditions in slight_rain:
                target_pos = SLIGHT_RAIN_POS
                effect_func = rain_effect
                effect_params = {'speed': 0.8}
            elif conditions in rain_showers:
                target_pos = RAIN_SHOWERS_POS
                effect_func = rain_effect
                effect_params = {'speed': 0.6}
            elif conditions in moderate_rain:
                target_pos = MODERATE_RAIN_POS
                effect_func = rain_effect
                effect_params = {'speed': 0.5}
            elif conditions in heavy_rain:
                target_pos = HEAVY_RAIN_POS
                effect_func = rain_effect
                effect_params = {'speed': 0.3}
            elif conditions in thunderstorm:
                target_pos = THUNDERSTORM_POS
                effect_func = thunderstorm_effect
            elif conditions in snow:
                target_pos = SNOW_POS
                effect_func = snow_effect

        # Execute the move and animation
        if target_pos is not None and effect_func is not None:
            move_servo_slowly(target_pos)
            effect_func(animation_duration_ms, start_time, **effect_params)
        else:
            condition_text = WMO_CODES.get(conditions, "Unknown")
            print(f"Condition '{condition_text}' ({conditions}) not handled. No action taken.")
            sleep(5)
            
        last_condition = conditions
        first_weather_check = False
    else:
        print("Condition unchanged. Waiting for next check.")
        sleep(weather_check_interval / 1000)

def move_servo_slowly(target_position):
    global current_servo_position
    step = 1 if target_position > current_servo_position else -1
    for pos in range(current_servo_position, target_position + step, step):
        servo(pos)
        sleep(servospeed)
    current_servo_position = target_position

def servo(degrees):
    degrees = max(0, min(180, degrees + servo_offset))
    min_pulse_us = 500
    max_pulse_us = 2500
    duty = int((min_pulse_us + (max_pulse_us - min_pulse_us) * (degrees / 180)) / 20000 * 65535)
    servoPin.duty_u16(duty)

def initial_servo_sweep():
    print("Performing initial servo sweep...")
    move_servo_slowly(22)
    sleep(2)
    move_servo_slowly(95)
    sleep(2)
    move_servo_slowly(2)

# --- Main Program Loop ---
initial_servo_sweep()
try:
    while True:
        if connect():
            get_conditions()
            move()
        else:
            print("Wi-Fi disconnected. Will try again in 1 minute.")
            sleep(60)
except KeyboardInterrupt:
    print("Program stopped.")
    pixels.fill((0, 0, 0))
    pixels.show()

