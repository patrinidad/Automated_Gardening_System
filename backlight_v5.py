from smbus2 import SMBus

I2C_BUS = 1
RGB_ADDR = 0x30  # Grove LCD RGB-Backlight v5 backlight address

REG0 = 0x00  # enable / reset
REG4 = 0x04  # channel enable/timer control
REG6 = 0x06  # LED1 current (R)
REG7 = 0x07  # LED2 current (G)
REG8 = 0x08  # LED3 current (B)

bus = SMBus(I2C_BUS)

def _w(r, v):
    bus.write_byte_data(RGB_ADDR, r, v & 0xFF)

def backlight_on():
    _w(REG0, 0b00011000)  # EN_CTRL=11
    _w(REG4, 0x15)        # enable LED1/2/3

def set_rgb(r, g, b):
    _w(REG6, r)
    _w(REG7, g)
    _w(REG8, b)

def backlight_off():
    _w(REG4, 0x00)
    _w(REG0, 0x00)
