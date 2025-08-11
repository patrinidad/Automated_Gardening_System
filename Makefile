# Makefile for the Raspberry Pi with soil, temp, and humidity sensors; i2c comms

install:
	echo "Updating apt packages..."
	sudo apt-get update
	echo "Installing dependencies for the garden..."
	sudo apt install -y python3 python3-pip python3-smbus i2c-tools
	echo "Installing Python libraries"
	pip3 install --upgrade pip
	pip3 install adafruit-blinka adafruit-circuitpython-dht RPi.GPIO smbus2 paho-mqtt
	echo "I2C interface in the Raspberry Pi must be enabled. See command sudo raspi-config"
	echo "ads7830.py must be present in this directory. See repository"

clean:
	echo "Uninstalling Python libraries from the garden"
	pip3 uninstall -y adafruit-blinka adafruit-circuitpython-dht RPi.GPIO smbus2 paho-mqtt
	echo "Tilling the garden is complete"

reinstall:
	make clean
	make install

