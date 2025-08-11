# ads7830.py
from smbus2 import SMBus

class ADS7830:
    def __init__(self, address=0x4b, bus_num=1):
        self.address = address
        self.bus = SMBus(bus_num)

    def read_channel(self, ch):  # ch = 0~7
        assert 0 <= ch <= 7
        cmd = 0x84 | (ch << 4)
        val = self.bus.read_byte_data(self.address, cmd)
        return val
