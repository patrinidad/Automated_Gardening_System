#!/home/pi/software/bin/python3
import sys
import time
import RPi.GPIO as GPIO

RELAY_GPIO = 17  
DURATION_S = 2.0  #decide how long (in seconds) the pump should run at button press


#relay
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_GPIO, GPIO.OUT, initial=GPIO.LOW)

try:
    GPIO.output(RELAY_GPIO, GPIO.HIGH)  #relay ON
    time.sleep(DURATION_S)
finally:
    GPIO.output(RELAY_GPIO, GPIO.LOW)   #relay OFF
    GPIO.cleanup()
