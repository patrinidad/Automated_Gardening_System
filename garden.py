#!/home/pi/software/bin/python3
import os
import time
import json
import board
import adafruit_dht
import RPi.GPIO as GPIO
from ads7830 import ADS7830

#mqtt initialize, same ssid as the Raspberry LCD!
#BROKER_IP = "ip_addr_here"   #phone hotspot preferred
#TOPIC = "garden/data"

#channel initialize
SOIL_CHANNEL = 0    #soil sensor signal pin on ADS7830 channel A0
DHT_PIN = board.D4  #GPIO4
RELAY_GPIO = 17     #GPIO17

#threshold initialize
SOIL_DRY_THRESHOLD = 60
SOIL_MOIST_THRESHOLD = 120

#relay initialize
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_GPIO, GPIO.OUT, initial=GPIO.LOW)  #start at OFF

def soil_condition(value):
    if value < SOIL_DRY_THRESHOLD:
        return "Dry"
    if value < SOIL_MOIST_THRESHOLD:
        return "Moist"
    return "Wet"

def relay_set(state): #HIGH = ON, LOW = OFF
    if state:
        GPIO.output(RELAY_GPIO, GPIO.HIGH)
    else:
        GPIO.output(RELAY_GPIO, GPIO.LOW)

def main():
    adc = ADS7830()
    dht = adafruit_dht.DHT11(DHT_PIN)

    #client.connect(BROKER_IP, 1883, 60) #for later, or remove if anything. mqtt comms

    try:
        while True:
            #os.system('clear') #uncomment if you dont wanna debug

            # read soil 
            soil_data = adc.read_channel(SOIL_CHANNEL)
            soil_status = soil_condition(soil_data)

            if soil_status == "Dry":
                relay_set(True)
            else:
                relay_set(False)

            # read DHT 
            try:
                temperature = dht.temperature
                humidity = dht.humidity
            except RuntimeError:
                temperature = None
                humidity = None

            # Print output
            print("---- Sensor Readings ----")
            print(f"Soil: {soil_status}")
            if humidity is not None and temperature is not None:
                print(f"Temp: {temperature: .1f} Celcius   Humidity: {humidity: .1f}%")
            else:
                print("Standby")
            
            #publish JSON for tx, Raspberry LCD for rx
            payload = {
                "soil_status": soil_status,
                "humidity": None if humidity is None else round(humidity, 1),
                "temperature": None if temperature is None else round(temperature, 1),
            }
            #client.publish(TOPIC, json.dumps(payload), qos=0, retain=False)
                
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nExiting...\n")
    finally:
        dht.exit()
        relay_set(False)
        GPIO.cleanup()

if __name__ == "__main__":
    main()
