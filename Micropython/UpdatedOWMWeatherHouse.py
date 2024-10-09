import time
import network
import urequests
from machine import Pin, PWM
from neopixel import Neopixel
import random
from time import sleep

# --- Configuration ---

# Replace with your Wi-Fi network credentials
ssid = 'your_wifi_ssid'          # Your Wi-Fi SSID
password = 'your_wifi_password'  # Your Wi-Fi password

# Replace with your OpenWeatherMap API key and location coordinates
api_key = "your_openweathermap_api_key"  # Your OpenWeatherMap API key
lat = "your_latitude"                    # Your latitude
lon = "your_longitude"                   # Your longitude

# Servo configuration
servospeed = 0.02     # Speed of the servo movement (seconds per degree)
sun_position = 150    # Servo position representing the sun
moon_position = 15    # Servo position representing the moon

# Neopixel configuration
numpix = 10           # Number of neopixels in the strip
pixels_pin = 28       # GPIO pin connected to the neopixel strip
toplight_pin = 17     # GPIO pin connected to the top light neopixel

# Brightness settings
day_brightness = 0.5   # Reduced brightness during the day for subtlety
night_brightness = 0.2 # 20% brightness during the night

# --- Initialization ---

# Initialize the servo PWM
servoPin = PWM(Pin(16))  # Initialize PWM on GPIO pin 16
servoPin.freq(50)        # Set frequency to 50Hz for servo control

# Initialize the current servo position
current_servo_position = 0  # Starting position of the servo

# Initialize Wi-Fi interface
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Initialize Neopixels
pixels = Neopixel(numpix, 0, pixels_pin, "GRB")  # Initialize neopixel strip
toplight = Neopixel(1, 1, toplight_pin, "RGBW")  # Initialize top light neopixel

# Define colors
OFF = (0, 0, 0)              # Color for turning off neopixels
WHITE = (255, 255, 255)      # White color
BLUE = (0, 0, 255)           # Blue color
LIGHT_BLUE = (0, 0, 128)     # Softer blue color for rain
YELLOW = (249, 215, 28)      # Yellow color for sunlight
SOFT_YELLOW = (125, 108, 14) # Softer yellow for subtle sunlight

# --- Functions ---

def connect():
    """
    Connects to the Wi-Fi network using the provided SSID and password.
    Retries until a connection is established.
    """
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        # Wait for connection or fail
        max_wait = 15
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            print('Waiting for connection...')
            sleep(1)

        # Handle connection error
        if not wlan.isconnected():
            print('Network connection failed')
            sleep(5)
            connect()
        else:
            print('Connected')
            status = wlan.ifconfig()
            print('IP address:', status[0])

def get_conditions():
    """
    Retrieves weather conditions from OpenWeatherMap API and determines if it's night or day.
    Sets the global variables 'conditions' and 'night' accordingly.
    """
    global conditions
    global night

    print("Getting data from OpenWeatherMap...")

    # Build the API request URL
    url = (
        "https://api.openweathermap.org/data/3.0/onecall?"
        "lat={}&lon={}&appid={}&units=metric"
    ).format(lat, lon, api_key)

    # Send the request and parse the response
    response = urequests.get(url)
    data = response.json()
    response.close()
    print("Weather data received.")
    # Extract current weather conditions
    conditions = int(data["current"]["weather"][0]["id"])
    print("Current conditions ID:", conditions)

    # Determine if it's currently night or day
    current_time = data["current"]["dt"]
    sunrise = data["current"]["sunrise"]
    sunset = data["current"]["sunset"]

    if current_time >= sunset or current_time <= sunrise:
        night = True
        print("It is currently night time.")
    else:
        night = False
        print("It is currently day time.")

def iconlight():
    """
    Controls the top light icon, turning it off and then on after a delay.
    """
    toplight.set_pixel(0, (0, 0, 0, 0))  # Turn off the top light
    toplight.show()
    print("Top light turned off.")
    sleep(3)  # Wait for 3 seconds
    toplight.set_pixel(0, (0, 0, 0, 100))  # Turn on the top light with brightness 100
    toplight.show()
    print("Top light turned on.")

def servo(degrees):
    """
    Moves the servo to a specified angle.
    Degrees should be between 0 and 180.
    """
    # Limit degrees to between 0 and 180
    degrees = max(0, min(180, degrees))
    # Set max and min duty cycles for the servo
    maxDuty = 1000
    minDuty = 9000
    # Calculate new duty cycle proportional to the desired angle
    newDuty = int(minDuty + (maxDuty - minDuty) * (degrees / 180))
    # Set the servo PWM duty cycle
    servoPin.duty_u16(newDuty)

def move_servo_slowly(target_position):
    """
    Moves the servo to the target position slowly, in increments.
    """
    global current_servo_position
    # Ensure target position is within limits
    target_position = max(0, min(180, target_position))
    step = 1  # Degrees per step
    delay = servospeed  # Delay between steps

    if current_servo_position < target_position:
        # Move servo upwards
        for pos in range(current_servo_position, target_position + 1, step):
            servo(pos)
            sleep(delay)
            current_servo_position = pos
    elif current_servo_position > target_position:
        # Move servo downwards
        for pos in range(current_servo_position, target_position - 1, -step):
            servo(pos)
            sleep(delay)
            current_servo_position = pos
    # If positions are equal, do nothing

def initial_servo_sweep():
    """
    Performs an initial sweep of the servo from sun position to moon position.
    """
    global current_servo_position
    # Move to sun position
    print("Moving servo to sun position.")
    move_servo_slowly(sun_position)
    sleep(5)  # Pause for 5 seconds
    # Move to moon position
    print("Moving servo to moon position.")
    move_servo_slowly(moon_position)
    sleep(5)  # Optional pause after reaching moon position

def sunny(duration_ms, start_time):
    """
    Displays a subtle sunny animation on the neopixel strip.
    """
    brightness = night_brightness if night else day_brightness
    color = tuple(int(c * brightness) for c in SOFT_YELLOW)
    while time.ticks_diff(time.ticks_ms(), start_time) < duration_ms:
        # Gentle pulsing effect
        for i in range(0, 100, 2):  # Fade in
            factor = i / 100
            r = int(color[0] * factor)
            g = int(color[1] * factor)
            b = int(color[2] * factor)
            pixels.fill((r, g, b))
            pixels.show()
            sleep(0.05)
        for i in range(100, -1, -2):  # Fade out
            factor = i / 100
            r = int(color[0] * factor)
            g = int(color[1] * factor)
            b = int(color[2] * factor)
            pixels.fill((r, g, b))
            pixels.show()
            sleep(0.05)

def rain(duration_ms, start_time):
    """
    Displays a subtle rain animation on the neopixel strip.
    """
    brightness = night_brightness if night else day_brightness
    # Use a softer blue color
    color = tuple(int(c * brightness) for c in LIGHT_BLUE)
    # Slow down the animation
    drop_speed = 0.5  # Time between drops
    pixels.fill(OFF)
    pixels.show()
    num_drops = 2  # Fewer raindrops for subtlety
    raindrops = [{'position': random.randint(0, numpix - 1)} for _ in range(num_drops)]

    while time.ticks_diff(time.ticks_ms(), start_time) < duration_ms:
        pixels.fill(OFF)
        for drop in raindrops:
            # Move drop down
            drop['position'] = (drop['position'] + 1) % numpix
            pixels.set_pixel(drop['position'], color)
        pixels.show()
        sleep(drop_speed)

def thunderstorm(duration_ms, start_time):
    """
    Displays a subtle thunderstorm animation on the neopixel strip.
    """
    brightness = night_brightness if night else day_brightness
    # Use softer flashes and longer intervals
    lightning_color = tuple(int(200 * brightness),) * 3
    while time.ticks_diff(time.ticks_ms(), start_time) < duration_ms:
        # Simulate rain
        rain_start_time = time.ticks_ms()
        rain(2000, rain_start_time)  # Rain for 2 seconds
        # Random chance of lightning
        if random.randint(0, 10) > 8:
            # Lightning flash
            pixels.fill(lightning_color)
            pixels.show()
            sleep(0.1)
            pixels.fill(OFF)
            pixels.show()
            sleep(random.uniform(0.5, 1.0))  # Longer interval before next flash

def moving_clouds(duration_ms, start_time):
    """
    Displays a subtle moving clouds animation on the neopixel strip.
    """
    brightness = night_brightness if night else day_brightness
    # Use softer gray colors
    cloud_colors = [
        (int(20 * brightness), int(20 * brightness), int(20 * brightness)),
        (int(40 * brightness), int(40 * brightness), int(40 * brightness)),
        (int(60 * brightness), int(60 * brightness), int(60 * brightness)),
        (int(40 * brightness), int(40 * brightness), int(40 * brightness))
    ]
    while time.ticks_diff(time.ticks_ms(), start_time) < duration_ms:
        for shift in range(numpix):
            if time.ticks_diff(time.ticks_ms(), start_time) >= duration_ms:
                break
            for i in range(numpix):
                color = cloud_colors[(i + shift) % len(cloud_colors)]
                pixels.set_pixel(i, color)
            pixels.show()
            sleep(0.5)  # Slow down the movement

def snow(duration_ms, start_time):
    """
    Displays a subtle snow animation on the neopixel strip.
    """
    brightness = night_brightness if night else day_brightness
    pixels.fill(OFF)
    pixels.show()
    num_flakes = 2  # Fewer snowflakes for subtlety
    snowflakes = [{'position': random.randint(0, numpix - 1)} for _ in range(num_flakes)]

    while time.ticks_diff(time.ticks_ms(), start_time) < duration_ms:
        pixels.fill(OFF)
        for flake in snowflakes:
            # Move flake down slowly
            if random.choice([True, False]):  # Move flake every other cycle
                flake['position'] = (flake['position'] + 1) % numpix
            flake_brightness = int(150 * brightness)
            pixels.set_pixel(flake['position'], (flake_brightness,) * 3)
        pixels.show()
        sleep(0.7)  # Slow down the animation

def clear_night(duration_ms, start_time):
    """
    Displays a subtle clear night (twinkling stars) animation on the neopixel strip.
    """
    brightness = night_brightness
    pixels.fill(OFF)
    pixels.show()
    num_stars = numpix // 3  # Fewer stars for subtlety

    # Generate unique random positions for stars
    star_positions = []
    while len(star_positions) < num_stars:
        pos = random.randint(0, numpix - 1)
        if pos not in star_positions:
            star_positions.append(pos)

    star_brightness = [random.randint(10, 30) for _ in range(num_stars)]
    star_directions = [random.choice([-1, 1]) for _ in range(num_stars)]
    
    while time.ticks_diff(time.ticks_ms(), start_time) < duration_ms:
        for i, pos in enumerate(star_positions):
            # Update brightness
            star_brightness[i] += star_directions[i] * random.randint(1, 2)
            # Reverse direction if limits are reached
            if star_brightness[i] >= 30:
                star_brightness[i] = 30
                star_directions[i] = -1
            elif star_brightness[i] <= 10:
                star_brightness[i] = 10
                star_directions[i] = 1
            # Set pixel color
            b = int(star_brightness[i] * brightness)
            pixels.set_pixel(pos, (b, b, b))
        pixels.show()
        sleep(1.0)  # Slow down the twinkling

def move():
    """
    Determines the weather conditions and triggers the appropriate servo and lighting animations.
    """
    global current_servo_position
    animation_duration_ms = 900000  # 15 minutes in milliseconds
    start_time = time.ticks_ms()

    # Weather condition codes
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

    if conditions in sunny_codes and not night:
        move_servo_slowly(sun_position)
        print("Moving servo to sunny position.")
        sunny(animation_duration_ms, start_time)
    elif conditions in sunny_codes and night:
        move_servo_slowly(moon_position)
        print("Moving servo to clear night position.")
        clear_night(animation_duration_ms, start_time)
    elif conditions in scatteredclouds:
        move_servo_slowly(130)
        print("Moving servo to scattered clouds position.")
        moving_clouds(animation_duration_ms, start_time)
    elif conditions in cloudy:
        move_servo_slowly(115)
        print("Moving servo to cloudy position.")
        moving_clouds(animation_duration_ms, start_time)
    elif conditions in showers or conditions in lightrain or conditions in moderaterain or conditions in heavyrain:
        move_servo_slowly(105)
        print("Moving servo to rain position.")
        rain(animation_duration_ms, start_time)
    elif conditions in snow_codes:
        move_servo_slowly(70)
        print("Moving servo to snow position.")
        snow(animation_duration_ms, start_time)
    elif conditions in thunderstorm_codes:
        move_servo_slowly(105)
        print("Moving servo to thunderstorm position.")
        thunderstorm(animation_duration_ms, start_time)
    elif conditions in haze or conditions in fog:
        move_servo_slowly(68)
        print("Moving servo to haze/fog position.")
        moving_clouds(animation_duration_ms, start_time)
    else:
        pixels.fill(OFF)
        pixels.show()
        print("No matching weather conditions found.")
        # Wait for the duration before checking again
        while time.ticks_diff(time.ticks_ms(), start_time) < animation_duration_ms:
            sleep(1)

# --- Main Program ---

# Perform initial servo sweep
initial_servo_sweep()

# Main loop
while True:
    connect()
    get_conditions()
    iconlight()
    move()
    # The 'move' function handles the waiting period before the next update
