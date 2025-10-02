# Final Version: 26th September 2025
# This version ensures the light animation runs continuously and uses a
# simplified day/night brightness control for the main LEDs.

import time
import network
import urequests
from machine import Pin, PWM
from neopixel import Neopixel
import random
from time import sleep, ticks_ms, ticks_diff
import ujson
import math

# --- Network Configuration ---
ssid = '' #Your Wifi ID
password = '' #Password
lat = "52.629238" #Your Latitude
lon = "0.492520" #Your Longitude 

# --- Calibrated Servo Positions ---
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
HEAVY_RAIN_POS = 95
RAIN_NIGHT_POS = 150
THUNDERSTORM_POS = 50
SNOW_POS = 135

# --- Neopixel LED Configuration ---
numpix = 10
pixels_pin = 28
pixels = Neopixel(numpix, 0, pixels_pin, "GRB")
toplight = Neopixel(1, 1, 17, "RGBW")
NIGHT_LIGHT_COLOR = (50, 50, 50, 50)
day_brightness = 0.2 # Set from 0.0 (off) to 1.0 (full brightness)
night_brightness = 0.2 # Set from 0.0 (off) to 1.0 (full brightness)
current_led_color = (0, 0, 0)

# --- Weather Update Configuration ---
weather_check_interval = 5 * 60 * 1000
last_weather_check = 0
conditions = 0
night = False
last_condition = None
first_weather_check = True
last_night_status = None

# --- WMO Weather Code Mapping ---
WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Rime fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Dense drizzle", 61: "Slight rain", 63: "Rain", 65: "Heavy rain",
    80: "Slight showers", 81: "Showers", 82: "Violent showers", 95: "Thunderstorm", 96: "Thunderstorm + Hail",
    71: "Slight snow", 73: "Snow", 75: "Heavy snow", 85: "Slight snow showers", 86: "Heavy snow showers"
}

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

# --- Hardware Initialization ---
servoPin = PWM(Pin(16))
servoPin.freq(50)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
current_servo_position = 90

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
            
            if night:
                toplight.set_pixel(0, NIGHT_LIGHT_COLOR)
            else:
                toplight.set_pixel(0, (0, 0, 0, 0))
            toplight.show()
            
            condition_text = WMO_CODES.get(conditions, "Unknown")
            print(f"Weather updated: {condition_text} ({conditions}), Night: {night}")
            last_weather_check = ticks_ms()
        except Exception as e:
            print(f"Failed to fetch weather data: {e}")

# --- Fade & Lighting Effects ---
def fade_to_color(target_color, duration_ms=500):
    global current_led_color
    steps = 50
    delay = duration_ms / steps
    start_color = current_led_color
    for i in range(steps + 1):
        r = int(start_color[0] + (target_color[0] - start_color[0]) * (i / steps))
        g = int(start_color[1] + (target_color[1] - start_color[1]) * (i / steps))
        b = int(start_color[2] + (target_color[2] - start_color[2]) * (i / steps))
        intermediate_color = (r, g, b)
        pixels.fill(intermediate_color)
        pixels.show()
        sleep(delay / 1000)
    current_led_color = target_color

def clear_day_effect(duration_ms, start_time, **kwargs):
    b = day_brightness
    target_color = (int(249 * b), int(215 * b), int(28 * b))
    fade_to_color(target_color)
    while ticks_diff(ticks_ms(), start_time) < duration_ms:
        sleep(1)

def clear_night_effect(duration_ms, start_time, **kwargs):
    b = night_brightness
    target_color = (int(150 * b), int(150 * b), int(255 * b))
    fade_to_color(target_color)
    while ticks_diff(ticks_ms(), start_time) < duration_ms:
        sleep(1.0)

def clouds_effect(duration_ms, start_time, **kwargs):
    b = night_brightness if night else day_brightness
    target_color = (int(30 * b), int(30 * b), int(30 * b))
    fade_to_color(target_color)
    while ticks_diff(ticks_ms(), start_time) < duration_ms:
        sleep(0.5)

def rain_effect(duration_ms, start_time, speed=0.1, **kwargs):
    global current_led_color
    splashes = []
    led_brightness = [0.0] * numpix
    start = ticks_ms()
    while ticks_diff(ticks_ms(), start) < duration_ms:
        for i in range(numpix): led_brightness[i] *= 0.95
        if random.random() < speed:
            splashes.append({"position": random.uniform(0, numpix - 1), "brightness": 1.0})
        for i in range(len(splashes) - 1, -1, -1):
            if splashes[i]["brightness"] < 0.01: splashes.pop(i)
            else: splashes[i]["brightness"] *= 0.9
        new_brightness = [0.0] * numpix
        for splash in splashes:
            for i in range(numpix):
                dist = abs(splash["position"] - i)
                b_splash = math.exp(-(dist * dist) / (2 * 1.5 * 1.5)) * splash["brightness"]
                new_brightness[i] += b_splash
        for i in range(numpix):
            b = max(led_brightness[i], new_brightness[i])
            led_brightness[i] = b
            final_b = b * (night_brightness if night else day_brightness)
            if final_b > 0.05: pixels.set_pixel(i, (int(10*final_b), int(50*final_b), int(255*final_b)))
            else: pixels.set_pixel(i, (0, 0, 0))
        pixels.show()
        sleep(0.02)
    current_led_color = (0, 0, 0)

def thunderstorm_effect(duration_ms, start_time, **kwargs):
    start = ticks_ms()
    while ticks_diff(ticks_ms(), start) < duration_ms:
        rain_effect(1000, ticks_ms(), speed=0.5)
        if random.randint(0, 10) > 8:
            # Lightning flash is always full brightness for impact
            pixels.fill((200, 200, 255)); pixels.show(); sleep(0.05)
            pixels.fill((0,0,0)); pixels.show(); sleep(0.05)

def fog_effect(duration_ms, start_time, **kwargs):
    b = (night_brightness if night else 0.3) * (day_brightness) # Fog is dimmer in day
    target_color = (int(80 * b), int(80 * b), int(80 * b))
    fade_to_color(target_color)
    while ticks_diff(ticks_ms(), start_time) < duration_ms:
        sleep(1.0)

def snow_effect(duration_ms, start_time, **kwargs):
    b = night_brightness if night else day_brightness
    snow_color = (int(255*b), int(255*b), int(255*b))
    snowflakes = [{'p': random.uniform(0,numpix-1),'s':random.uniform(0.02,0.05)} for _ in range(4)]
    start = ticks_ms()
    while ticks_diff(ticks_ms(), start) < duration_ms:
        pixels.fill((0, 0, 0))
        for flake in snowflakes:
            flake['p'] += flake['s']
            if flake['p'] > numpix: flake['p'] = 0
            pixels.set_pixel(int(flake['p']), snow_color)
        pixels.show()
        sleep(0.05)

# --- REFACTORED Core Logic ---
def run_display_cycle():
    global last_condition, first_weather_check, last_night_status
    action_key = None
    if night:
        if conditions in clear_sky: action_key = "clear_night"
        elif conditions in partly_cloudy: action_key = "partly_cloudy_night"
        elif conditions in all_rain_types: action_key = "rain_night"
    if action_key is None:
        if conditions in clear_sky: action_key = "clear_day"
        elif conditions in partly_cloudy: action_key = "partly_cloudy_day"
        elif conditions in overcast: action_key = "overcast"
        elif conditions in fog: action_key = "fog"
        elif conditions in slight_rain: action_key = "slight_rain"
        elif conditions in rain_showers: action_key = "rain_showers"
        elif conditions in moderate_rain: action_key = "moderate_rain"
        elif conditions in heavy_rain: action_key = "heavy_rain"
        elif conditions in thunderstorm: action_key = "thunderstorm"
        elif conditions in snow: action_key = "snow"
    
    state_changed = first_weather_check or last_condition != conditions or last_night_status != night
    if state_changed: print(f"New change detected. Updating display.")
    else: print("Condition unchanged. Continuing animation.")

    if action_key:
        WEATHER_ACTIONS = {
            "clear_night": {"pos": CLEAR_NIGHT_POS, "effect": clear_night_effect},
            "partly_cloudy_night": {"pos": PARTLY_CLOUDY_NIGHT_POS, "effect": clouds_effect},
            "rain_night": {"pos": RAIN_NIGHT_POS, "effect": rain_effect, "params": {'speed': 0.2}},
            "clear_day": {"pos": CLEAR_DAY_POS, "effect": clear_day_effect},
            "partly_cloudy_day": {"pos": PARTLY_CLOUDY_POS, "effect": clouds_effect},
            "overcast": {"pos": OVERCAST_POS, "effect": clouds_effect},
            "fog": {"pos": FOG_POS, "effect": fog_effect},
            "slight_rain": {"pos": SLIGHT_RAIN_POS, "effect": rain_effect, "params": {'speed': 0.1}},
            "rain_showers": {"pos": RAIN_SHOWERS_POS, "effect": rain_effect, "params": {'speed': 0.2}},
            "moderate_rain": {"pos": MODERATE_RAIN_POS, "effect": rain_effect, "params": {'speed': 0.35}},
            "heavy_rain": {"pos": HEAVY_RAIN_POS, "effect": rain_effect, "params": {'speed': 0.5}},
            "thunderstorm": {"pos": THUNDERSTORM_POS, "effect": thunderstorm_effect},
            "snow": {"pos": SNOW_POS, "effect": snow_effect}
        }
        action = WEATHER_ACTIONS[action_key]
        if state_changed: move_servo_slowly(action["pos"])
        action["effect"](weather_check_interval, ticks_ms(), **action.get("params", {}))
    else:
        condition_text = WMO_CODES.get(conditions, "Unknown")
        print(f"Condition '{condition_text}' ({conditions}) not handled.")
        sleep(5)
            
    last_condition = conditions
    last_night_status = night
    first_weather_check = False

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
    move_servo_slowly(22); sleep(2)
    move_servo_slowly(95); sleep(2)
    move_servo_slowly(2)

# --- Main Program Loop ---
initial_servo_sweep()
try:
    while True:
        if connect():
            get_conditions()
            run_display_cycle()
        else:
            print("Wi-Fi disconnected. Will try again in 1 minute.")
            sleep(60)
except KeyboardInterrupt:
    print("Program stopped by user.")
    pixels.fill((0, 0, 0)); pixels.show()
    toplight.set_pixel(0, (0,0,0,0)); toplight.show()

