# TinyCircuits A1454 Analog Hall Python Package
# Written by: Laverena Wienclaw for TinyCircuits
# Initialized: Jan 2020
# Last updated: Jan 2020

import pigpio 

_A1454_ADDRESS        = 0x60
_A1454_ACCESS_ADDRESS = 0x24
_A1454_ACCESS_CODE    = 0x2C413534
_A1454_TEMPOUT        = 0x1D
_A1454_OUTPUT         = 0x1F
_A1454_SLEEP          = 0x20

class A1454:
    def __init__(self):
        # Init variables
        self.mag = None
        self.temp = None

    def readMag(self):    
        pi = pigpio.pi()
        h = pi.i2c_open(1, _A1454_ADDRESS)
        pi.i2c_write_byte(h, _A1454_OUTPUT)

        # Request 4 data bytes
        (b, d) = pi.i2c_read_i2c_block_data(h, _A1454_OUTPUT, 4)
        pi.i2c_close(h)       
        x = d[2]
        y = d[3]

        x <<= 12
        x = x | (y << 4)
        x >>= 4
        x = self.twos_comp(x, 12)
        x = x / 4.0 / 10.0

        self.mag = x
        return self.mag

    def readTemp(self):    
        pi = pigpio.pi()
        h = pi.i2c_open(1, _A1454_ADDRESS)
        pi.i2c_write_byte(h, _A1454_TEMPOUT)

        # Request 4 data bytes
        (b, d) = pi.i2c_read_i2c_block_data(h, _A1454_TEMPOUT, 4)
        pi.i2c_close(h)       
        x = d[2]
        y = d[3]

        x <<= 12
        x |= (y << 4)
        x >>= 4
        x = self.twos_comp(x, 12)
        x /= 8
        x += 25

        self.temp = x
        return self.temp

    def twos_comp(self, val, bits):
        # compute the 2's complement of int value val
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return val  
