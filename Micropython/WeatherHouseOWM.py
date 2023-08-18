import time
import network, usocket, utime, ntptime
import machine
from machine import Pin, PWM
import urequests
from time import sleep
from time import gmtime
from neopixel import Neopixel
import random
from random import randint

#Set Up Wifi Connection

ssid = 'YOURSSID'
password = 'YOURWIFIPASSWORD'


#Set Open Weather Map API

def get_conditions():
    
    global hour
    global conditions

   
    print ("Getting Data from Open Weather Map")

    api_key = "YOURAPIKEY"
    lat = "YOURLAT"
    lon = "YOURLONG"
    url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api_key)
    response = urequests.get(url)
    data = response.json()
    print(data)
    conditions = int(data ["current"]["weather"][0]["id"])
    print("Current Conditions = ", conditions)
    
#Get time to determine if its nigh or day
    
detailed_time = gmtime()

print (detailed_time)

global night

global hour

def night():
    
    global night
    hour = (detailed_time[3])
    print("Hour = ", hour)
    if hour >= 20 or hour <= 6:
        night = 1
        print ("Night = ", night)
    else:
        night = 0
        print ("Night = ", night)

# Set up Servo Speed and Range

servospeed = 0.05 #Speed of the servo movement - 0.05 provides a good smooth speed
servorange = 155 #Edit for the range of the servo, the Lego Non Continuous is Approx 155 Degrees for a 360 sweep.


# Set up Servo Pins and Data Range
servoPin = PWM(Pin(16))
servoPin.freq(50)

servorange = 155

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Connect to Wifi

def connect():
    wlan.connect(ssid, password)
    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

# Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
        connect()
    else:
        print('connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )
    
#Set Up Neopixels
        

#Set up Neopixels Bottom Stip
numpix = 10 #number of neopixels to the sweep the servo
pixels = Neopixel(numpix, 0, 28, "GRB")
toplight = Neopixel(1, 1, 17, "RGBW")
#TopLight


#Set Colours for Bottom Strip
OFF = (0, 0, 0)
WHITE = (20, 20, 20,) #255 is full brightness - not recommended due to power draw
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (249, 215, 28)

#Set up Single Neopixels for Top Light

def iconlight():
    toplight.set_pixel(0, (0, 0, 0, 0))
    toplight.show()
    print("Top Light Off")
    sleep(3)
    toplight.set_pixel(0, (0, 0, 0, 10))
    toplight.show()
    print("Top Light On")
    toplight.show()

#Set Up Lights for Conditions
    
    
def partly_cloudy():
    
    pixels.fill((WHITE))
    pixels.show()


def moving_clouds():
    for i in range(256):
        r = int(color[0] * i / 255)
        g = int(color[1] * i / 255)
        b = int(color[2] * i / 255)
        for j in range(numpix):
            if j % 2 == 0:
                pixels.set_pixel(j, (r, g, b))
            else:
                pixels.set_pixel(j, (200, 200, 200))
        pixels.show()
        sleep(duration / 256)

def sun():
    for i in range(256):
        r = int(color[0] * i / 255)
        g = int(color[1] * i / 255)
        b = int(color[2] * i / 255)
        for j in range(numpix):
            if j % 2 == 0:
                pixels.set_pixel(j, (r, g, 0))
            else:
                pixels.set_pixel(j, (r, g, b))
        pixels.show()
        sleep(duration / 256)

def someclouds():
    
        partly_cloudy((255, 255, 255), 30)
        sun((255, 255, 100), 30)
        moving_clouds((255, 255, 255), 30)
        sun((255, 255, 100), 3)
        moving_clouds((255, 255, 255), 30)
        partly_cloudy((255, 255, 255), 30)
        sun((255, 255, 100), 30)
        moving_clouds((255, 255, 255), 30)
        sun((255, 255, 100), 30)

def rain():
    toplight.set_pixel(0, (20, 20, 20, 0))
    toplight.show()

    print("Top Light Dimmed - Rain")
    toplight.show()
    pixels.set_pixel(6, (OFF))
    pixels.show()
    pixels.set_pixel(0, (OFF))
    pixels.show()
    n = 0
    while n < 300:
        pixelnum = random.randint(0, 8)
        bright = random.randint(10, 100)
        pixels.brightness(bright)
        Rain = [(0, 0, 255), (0, 0, 200), (0, 0, 50),(0, 20, 100)]
        pixels.set_pixel(pixelnum, (random.choice(Rain)))
        pixels.set_pixel((pixelnum-1), (OFF))
        pixels.show()  
        sleep(random.uniform(.8, .2))
        n = n+1

def snow():
    n = 0
    while n < 300:
        pixelnum = random.randint(0, 8)
        bright = random.randint(10, 100)
        pixels.brightness(bright)
        Snow = [(255, 255, 255), (50, 50, 50), (2, 20, 20),(125, 125, 125)]
        pixels.set_pixel(pixelnum, (random.choice(Snow)))
        pixels.set_pixel((pixelnum-1), (OFF))
        pixels.show()  
        sleep(random.uniform(.8, .2))
        print(n)
        n = n+1
        
def thunderstorm():
  n = 0
  while n < 100:
  
    for i in range (random.randint(10, 100)):
        pixelnum = random.randint(0, 8)
        Rain = [(0, 0, 255), (0, 0, 200), (0, 0, 50),(0, 20, 100)]
        pixels.set_pixel(pixelnum, (random.choice(Rain)))
        pixels.brightness(i)
        pixels.show()
        sleep(random.uniform(.05, .1))
        pixels.set_pixel(pixelnum, (OFF))
        pixels.show()
    for i in range (random.randint(10, 100) -1):
        pixelnum = random.randint(0, 8)
        Rain = [(0, 0, 255), (0, 0, 20), (0, 0, 50),(0, 20, 100)]
        pixels.set_pixel(pixelnum, (random.choice(Rain)))
        pixels.brightness(i)
        sleep(random.uniform(.05, .1))
        pixels.set_pixel(pixelnum, (OFF))
        pixels.show()
    for i in range (random.randint(10, 100)):
        pixelnum = random.randint(0, 8)
        Thunder = [(255, 255, 255), (255, 255, 200), (255, 255, 50),(255, 255, 0)]
        pixels.set_pixel(pixelnum, (random.choice(Thunder)))
        pixels.brightness(i)
        pixels.show()
        sleep(random.uniform(.05, .1))
        pixels.set_pixel(pixelnum, (OFF))
        pixels.show()
    for i in range (random.randint(10, 100) -1):
        pixelnum = random.randint(0, 8)
        Thunder = [(255, 255, 255), (255, 255, 200), (255, 255, 50),(255, 255, 0)]
        pixels.set_pixel(pixelnum, (random.choice(Thunder)))
        pixels.brightness(i)
        sleep(random.uniform(.05, .1))
        pixels.set_pixel(pixelnum, (OFF))
        pixels.show()
    
    n = n+1
  
def sunny():
    n = 0
    pixels.fill((OFF))
    pixels.show()
    sleep(2)
    while n < 300:
        pixels.fill((YELLOW))
        pixels.show()
        sleep(1)
        print(n)
        n = n+1
    


def servo(degrees):
    # limit degrees beteen 0 and 180
    if degrees > 180: degrees=180
    if degrees < 0: degrees=0
    # set max and min duty
    #Reverse order below to change direction according to servo setup
    maxDuty=1000
    minDuty=9000
    
    # new duty is between min and max duty in proportion to its value
    newDuty=minDuty+(maxDuty-minDuty)*(degrees/180)
    # servo PWM value is set
    servoPin.duty_u16(int(newDuty))


# First Sweep - Degree Range to be Edited According to Servo for Setup

def sweep():
    n= 0
    while n < servorange :
      
        servo(n)
        sleep(servospeed)
        n = n+1
        
    sleep(5)    
    n = servorange
    while n >= 1 :
      
        servo(n)
        sleep(servospeed)
        n = n-1
    sleep(5)
        
# Set up Servo Position and Lighting for Conditions

def move():

# Code Ranges
    
    sunny = [800]
    fewclouds = [801]    
    scatteredclouds = [802,803]
    cloudy =[804]
    showers = [520,521,522,531]
    lightrain = [300,301,302,310,311,312,313,314,321, 500]
    moderaterain = [501]
    heavyrain = [501,502,503,504]
    thunderstorm = [200, 201, 202, 210, 211, 212, 221, 230, 231, 232]
    snow = [600,601,602,611,612,613,615,616,620,622]
    fog = [741]
    haze = [701,721]

    if conditions in sunny and night == 0:
        servo(150)
        sunny()
        print("Moving Servo to Sunny")

    if conditions in sunny and night == 1:
        servo(15)
        print("Moving Servo to Night Clear")

    if conditions in scatteredclouds and night == 0:
        servo(130)
        moving_clouds()
        print("Moving Servo to Scattered Clouds")

    if conditions in cloudy and night == 1:
        servo(115)
        print("Moving Servo to Night Clouds")

    if conditions in scatteredclouds and night == 1:
        servo(115)
        print("Moving Servo to Night Clouds")

    if conditions in showers:
        servo(30)
        print("Moving Servo to Showers")

    if conditions in cloudy and night == 0:
        servo(115)
        print("Moving Servo to Cloudy")
        partly_cloudy()

    if conditions in showers and night == 0:
        servo(125)
        rain()
        print("Moving Servo to Showers")

    if conditions in lightrain and night == 0:
        servo(105)
        rain()
        print("Moving Servo to Light Rain")
        
    if conditions in moderaterain and night == 0:
        servo(105)
        rain()
        print("Moving Servo to Light Rain")
        
    if conditions in heavyrain and night == 0:
        servo(105)
        rain()
        print("Moving Servo to Light Rain")
        
    if conditions in snow:
        servo(70)
        snow()
        print("Moving Servo to Snow")
             
    if conditions in haze:
        servo(68)
        print("Moving Servo to Haze")
               
    if conditions in fog:
        servo(68)
        print("Moving Servo to Fog")
        
        
    if conditions in thunderstorm:
        servo(105)
        thunderstorm()
        print("Moving Servo to Thunderstorm")

    else:
        pixels.fill(OFF)
        pixels.show()
        print("No conditions found")
     
while True:
    connect()
    iconlight()
    night()
    sweep()
    get_conditions()
    move()
    
    print("Waiting for next data request - Set for every 15 mins")
    time.sleep(900) #time to wait, in seconds, before getting data again
    
else:
    connect()
