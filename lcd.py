#!/home/pi/software/bin/python3
#main component for this is the Grove LCD RGB-Backlgiht JHD2202M1 
#this Pi connects to the Raspberry Pi with the sensors required for garden automation via SSH

import subprocess
import json
import time
import shlex
from smbus2 import SMBus
import RPi.GPIO as GPIO

BUTTON_PIN = 24  
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #button inital config

#ssh is the main method of comms
R1_USER = "pi"
R1_HOST = "10.0.0.2" 
R1_CMD  = "/home/pi/software/bin/python3 /home/pi/garden/garden3.py --json"
R1_PUMP_CMD = "/home/pi/software/bin/python3 /home/pi/garden/pump_remote.py 2"

# initalization LCD JHD2202M1 
I2C_BUS_NUM = 1
LCD_ADDR    = 0x3E

bus = SMBus(I2C_BUS_NUM)

def lcd_cmd(v):
    bus.write_byte_data(LCD_ADDR, 0x00, v & 0xFF)

def lcd_data(v):
    bus.write_byte_data(LCD_ADDR, 0x40, v & 0xFF)

def lcd_init():
    # Init sequence for AIP31068/HD44780-compatible I2C text LCDs
    time.sleep(0.05)
    lcd_cmd(0x38)  # Function set: 8-bit, 2 lines
    lcd_cmd(0x39)  # Extended instruction set
    lcd_cmd(0x14)  # Internal OSC
    lcd_cmd(0x70)  # Contrast (low bits) 0x70..0x7F if too light/dark
    lcd_cmd(0x5C)  # Power/ICON/Contrast (high bits) 0x5C..0x5F
    lcd_cmd(0x6C)  # Follower control (booster)
    time.sleep(0.2)
    lcd_cmd(0x38)  # Back to normal instruction set
    lcd_cmd(0x0C)  # Display ON, cursor OFF
    lcd_cmd(0x01)  # Clear
    time.sleep(0.002)

def lcd_set_cursor(row, col):
    base = 0x00 if row == 0 else 0x40
    lcd_cmd(0x80 | (base + col))

def lcd_write_line(text, row):
    s = (text or "")[:20].ljust(20)
    lcd_set_cursor(row, 0)
    for ch in s:
        lcd_data(ord(ch))

#writing info for each row
def row1(soil, hum):
    #outputs "Soil: Dry   H:55%"
    s = soil or "Unknown"
    if hum is None:
        h = "--%"
    else:
        try:
            h = f"{int(round(hum))}%"
        except Exception:
            h = "--%"
    return f"Soil: {s:<4} H:{h}"

def row2(temp):
    #outputs "Temp: 23.4 C"
    if temp is None:
        return "Temp: --.- C"
    try:
        return f"Temp: {float(temp):.1f} C"
    except Exception:
        return "Temp: --.- C"

def start_ssh_process():
    #no password prompts required if key-gen is established for this Pi to the sensor Pi (see ssh variables above)
    cmd = f"ssh -o BatchMode=yes -o ConnectTimeout=5 {R1_USER}@{R1_HOST} {shlex.quote(R1_CMD)}"
    return subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

def send_pump_override():
    cmd_pump = f"ssh -o BatchMode=yes -o ConnectTimeout=5 {R1_USER}@{R1_HOST} {shlex.quote(R1_PUMP_CMD)}"
    subprocess.run(cmd_pump, shell=True, check=False)

def check_manual_override():
    if GPIO.input(BUTTON_PIN) == GPIO.HIGH:  # button pressed
        send_pump_override()
        time.sleep(0.2)  # debounce



def main():
    lcd_init()
    lcd_write_line("Connecting to sensors...", 0)
    lcd_write_line("", 1)

    proc = None
    try:
        while True:
            check_manual_override()
            #try to see if ssh is running
            if proc is None or proc.poll() is not None:
                proc = start_ssh_process()
             
                lcd_write_line("Connecting to sensors...", 0)
                lcd_write_line("", 1)
                
                time.sleep(0.5)

            #initialize ssh stream
            line = proc.stdout.readline()
            if not line: 
                time.sleep(0.2)
                continue

            line = line.strip()

            #focus info on brackets that comes with json
            if not (line.startswith("{") and line.endswith("}")):
                continue

            # parse json and update the lcd with the info received
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue

            soil = msg.get("soil_status")
            hum  = msg.get("humidity")
            temp = msg.get("temperature")

            lcd_write_line(row1(soil, hum), 0)
            lcd_write_line(row2(temp), 1)

    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
        try:
            if proc and proc.poll() is None:
                proc.terminate()
        except Exception:
            pass
        bus.close()

if __name__ == "__main__":
    main()
