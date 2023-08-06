# TinyCircuits BMA250 Accelerometer Python Package
# Written by: Laverena Wienclaw for TinyCircuits
# Initialized: Jan 2020
# Last updated: Jan 2020

import pigpio 

_BMA250_I2CADDR          = 0x18
_BMA250_update_time_64ms = 0x08
_BMA250_update_time_32ms = 0x09
_BMA250_update_time_16ms = 0x0A
_BMA250_update_time_8ms  = 0x0B
_BMA250_update_time_4ms  = 0x0C
_BMA250_update_time_2ms  = 0x0D
_BMA250_update_time_1ms  = 0x0E
_BMA250_update_time_05ms = 0xF
_BMA250_range_2g         = 0x03
_BMA250_range_4g         = 0x05
_BMA250_range_8g         = 0x08
_BMA250_range_16g        = 0x0C

class BMA250: 
    def __init__(self, range, bandwidth):
        # Setup range measurement setting
        pi = pigpio.pi()
        h = pi.i2c_open(1, _BMA250_I2CADDR)
        pi.i2c_write_byte(h, 0x0F)
        pi.i2c_write_byte(h, range)
        pi.i2c_close(h)

        # Setup bandwidth
        pi = pigpio.pi()
        h = pi.i2c_open(1, _BMA250_I2CADDR)
        pi.i2c_write_byte(h, 0x10)
        pi.i2c_write_byte(h, bandwidth)
        pi.i2c_close(h)

        # Init Accel variables
        self.X = None
        self.Y = None
        self.Z = None
        self.Temp = None

    def readSensor(self):
        # Set register index
        pi = pigpio.pi()
        h = pi.i2c_open(1, _BMA250_I2CADDR)
        pi.i2c_write_byte(h, 0x02)

        # Request 7 data bytes (x-lsb, x-msb, y-lsb, y-msb, z-lsb, z-msb, rawTemp)
        (b, d) = pi.i2c_read_i2c_block_data(h, 0x02, 7)
        pi.i2c_close(h)
        if b>= 0:
           # print(d) # prints contents of all 7 registers
           self.X = d[0] | (d[1] << 8)
           self.X = self.X >> 6 # only use 10 significant bits
           if self.X > 511:
              self.X -=1024
           # print(self.X)

           self.Y = d[2] | (d[3] << 8)
           self.Y = self.Y >> 6
           if self.Y > 511:
              self.Y -=1024
           # print(self.Y)

           self.Z = d[4] | (d[5] << 8)
           self.Z = self.Z >> 6
           if self.Z > 511:
              self.Z -=1024
           # print(self.Z)

           self.Temp = d[6]
           self.Temp = ((self.Temp *0.5) +24)
           # print(self.Temp)
        else:
            print("There was an error reading the BMA250 register data")
