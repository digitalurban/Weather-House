import time
import network
import urequests
from machine import Pin, PWM
from neopixel import Neopixel
import random
from time import sleep, ticks_ms, ticks_diff

# --- Configuration ---

# Replace with your Wi-Fi network credentials
ssid = 'your_wifi_ssid'          # Your Wi-Fi SSID
password = 'your_wifi_password'  # Your Wi-Fi password

# Replace with your OpenWeatherMap API key and location coordinates
api_key = "your_openweathermap_api_key"  # Your OpenWeatherMap API key
lat = "your_latitude"                    # Your latitude
lon = "your_longitude"                   # Your longitude

# Servo Configuration
servospeed = 0.02
sun_position = 150
moon_position = 15
current_servo_position = 0
servo_offset = 0

# Neopixel Configuration
numpix = 10  # Number of LEDs in the strip
pixels_pin = 28  # GPIO pin for the Neopixel strip
pixels = Neopixel(numpix, 0, pixels_pin, "GRB")

# Top Light Configuration
toplight_pin = 17  # GPIO pin for the top light
toplight = Neopixel(1, 0, toplight_pin, "GRB")  # Initialize top light separately

# Brightness Settings
day_brightness = 0.5
night_brightness = 0.2

# Weather Update Interval
weather_check_interval = 15 * 60 * 1000  # 15 minutes
last_weather_check = 0
conditions = 800
night = False
last_condition = None
first_weather_check = True  # Flag to ensure the servo moves on the first check

# Weather Conditions
sunny_codes = [800]
fewclouds = [801]
scatteredclouds = [802, 803]
cloudy = [804]
showers = [520, 521, 522, 531]
lightrain = [300, 301, 302, 310, 311, 312, 313, 314, 321, 500]
moderaterain = [501]
heavyrain = [502, 503, 504]
thunderstorm_codes = [200, 201, 202, 210, 211, 212, 221, 230, 231, 232]
snow_codes = [600, 601, 602, 611, 612, 613, 615, 616, 620, 622]
fog = [741]
haze = [701, 721]

# Colors
OFF = (0, 0, 0)
YELLOW = (249, 215, 28)
LIGHT_BLUE = (0, 0, 128)
SOFT_GRAY = (30, 30, 30)
WHITE = (255, 255, 255)

# Initialize Servo
servoPin = PWM(Pin(16))
servoPin.freq(50)

# Wi-Fi Initialization
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Helper Functions
def connect():
    """Connect to Wi-Fi."""
    if not wlan.isconnected():
        print("Attempting to connect to Wi-Fi...")
        wlan.connect(ssid, password)
        for _ in range(15):
            if wlan.isconnected():
                print("Connected to Wi-Fi.")
                return True
            print("Waiting for Wi-Fi connection...")
            sleep(1)
        print("Failed to connect to Wi-Fi.")
        return False
    return True

def iconlight():
    """Toggle the top light as an indicator."""
    toplight.set_pixel(0, OFF)  # Turn off the top light
    toplight.show()
    sleep(3)  # Wait for 3 seconds
    toplight.set_pixel(0, (100, 100, 100))  # Turn on the top light
    toplight.show()
    print("Top light toggled on.")

def get_conditions():
    """Fetch weather conditions from OpenWeatherMap."""
    global conditions, night, last_weather_check
    if last_weather_check == 0 or ticks_diff(ticks_ms(), last_weather_check) >= weather_check_interval:
        print("Getting Data from OpenWeatherMap...")
        try:
            url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            response = urequests.get(url)
            data = response.json()
            response.close()
            conditions = int(data["current"]["weather"][0]["id"])
            current_time = data["current"]["dt"]
            sunrise = data["current"]["sunrise"]
            sunset = data["current"]["sunset"]
            night = current_time >= sunset or current_time <= sunrise
            last_weather_check = ticks_ms()
            print(f"Weather conditions updated: {conditions}, Night: {night}")
        except Exception as e:
            print(f"Failed to fetch weather data: {e}")
    else:
        print("Skipping weather update, not yet 15 minutes.")

# Ambient Lighting for Weather Conditions
def sunny(duration_ms, start_time):
    brightness = night_brightness if night else day_brightness
    while ticks_diff(ticks_ms(), start_time) < duration_ms:
        pixels.fill((int(YELLOW[0] * brightness), int(YELLOW[1] * brightness), int(YELLOW[2] * brightness)))
        pixels.show()
        sleep(1)

def moonlight(duration_ms, start_time):
    brightness = night_brightness
    moon_color = (int(150 * brightness), int(150 * brightness), int(255 * brightness))
    while ticks_diff(ticks_ms(), start_time) < duration_ms:
        pixels.fill(moon_color)
        pixels.show()
        sleep(1.0)

def scattered_clouds(duration_ms, start_time):
    brightness = night_brightness if night else day_brightness
    cloud_color = (int(SOFT_GRAY[0] * brightness), int(SOFT_GRAY[1] * brightness), int(SOFT_GRAY[2] * brightness))
    while ticks_diff(ticks_ms(), start_time) < duration_ms:
        pixels.fill(cloud_color)
        pixels.show()
        sleep(0.5)

def rain(duration_ms, start_time):
    brightness = night_brightness if night else day_brightness
    num_drops = 2
    raindrops = [{'position': random.randint(0, numpix - 1)} for _ in range(num_drops)]
    while ticks_diff(ticks_ms(), start_time) < duration_ms:
        pixels.fill(OFF)
        for drop in raindrops:
            drop['position'] = (drop['position'] + 1) % numpix
            pixels.set_pixel(drop['position'], (0, 0, int(128 * brightness)))
        pixels.show()
        sleep(0.7)

def thunderstorm(duration_ms, start_time):
    rain(duration_ms, start_time)
    if random.randint(0, 10) > 8:
        pixels.fill(WHITE)
        pixels.show()
        sleep(0.1)
        pixels.fill(OFF)
        pixels.show()

def fog_light(duration_ms, start_time):
    brightness = night_brightness
    fog_color = (int(50 * brightness), int(50 * brightness), int(50 * brightness))
    while ticks_diff(ticks_ms(), start_time) < duration_ms:
        pixels.fill(fog_color)
        pixels.show()
        sleep(1.0)

def snow(duration_ms, start_time):
    brightness = night_brightness
    snowflakes = [{'position': random.randint(0, numpix - 1)} for _ in range(2)]
    while ticks_diff(ticks_ms(), start_time) < duration_ms:
        pixels.fill(OFF)
        for flake in snowflakes:
            flake['position'] = (flake['position'] + 1) % numpix
            pixels.set_pixel(flake['position'], WHITE)
        pixels.show()
        sleep(0.8)

# Movement and Lighting
def move():
    global last_condition, first_weather_check
    animation_duration_ms = 900000  # 15 minutes
    start_time = ticks_ms()

    if first_weather_check or last_condition != conditions:
        if conditions in sunny_codes:
            if night:
                move_servo_slowly(moon_position)
                moonlight(animation_duration_ms, start_time)
            else:
                move_servo_slowly(sun_position)
                sunny(animation_duration_ms, start_time)
        elif conditions in scatteredclouds:
            move_servo_slowly(130)
            scattered_clouds(animation_duration_ms, start_time)
        elif conditions in showers or conditions in lightrain:
            move_servo_slowly(105)
            rain(animation_duration_ms, start_time)
        elif conditions in thunderstorm_codes:
            move_servo_slowly(105)
            thunderstorm(animation_duration_ms, start_time)
        elif conditions in fog or conditions in haze:
            move_servo_slowly(72)
            fog_light(animation_duration_ms, start_time)
        elif conditions in snow_codes:
            move_servo_slowly(70)
            snow(animation_duration_ms, start_time)
        else:
            print("No matching condition, turning off lights.")
            pixels.fill(OFF)
            pixels.show()
        last_condition = conditions
        first_weather_check = False
    else:
        print("Condition unchanged, skipping movement.")

# Servo Movement
def move_servo_slowly(target_position):
    global current_servo_position
    step = 1
    delay = servospeed
    target_position = max(0, min(180, target_position))
    if current_servo_position < target_position:
        for pos in range(current_servo_position, target_position + 1, step):
            servo(pos)
            sleep(delay)
            current_servo_position = pos
    elif current_servo_position > target_position:
        for pos in range(current_servo_position, target_position - 1, -step):
            servo(pos)
            sleep(delay)
            current_servo_position = pos

def servo(degrees):
    """Move the servo to a specific angle."""
    degrees = max(0, min(180, degrees + servo_offset))
    maxDuty = 1000
    minDuty = 9000
    newDuty = int(minDuty + (maxDuty - minDuty) * (degrees / 180))
    servoPin.duty_u16(newDuty)

# Initial Servo Sweep
def initial_servo_sweep():
    """Perform an initial sweep of the servo to set starting positions."""
    print("Performing initial servo sweep...")
    move_servo_slowly(sun_position)
    sleep(5)
    move_servo_slowly(moon_position)
    sleep(5)

# Main Program
initial_servo_sweep()

try:
    while True:
        if connect():
            if last_weather_check == 0 or ticks_diff(ticks_ms(), last_weather_check) >= weather_check_interval:
                iconlight()  # Toggle top light during weather update
                get_conditions()
            move()
        sleep(30)  # Prevent CPU overload by adding a brief pause
except KeyboardInterrupt:
    print("Program stopped.")

