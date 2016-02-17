#!/usr/bin/python
# -*- coding: utf-8 -*-
# ==================================================
# Bosch BMP085 pressure and temperature sensor 
# Datasheet: http://www.adafruit.com/datasheets/BMP085_DataSheet_Rev.1.0_01July2008.pdf
# ==================================================
#
# Very simple implementation
# ==================================================
    
from i2c_core import i2c_core

import time

class BMP085(object):

	# Define registers values from datasheet
	CALIB_BLOCK_ADDRESS = 0xAA
	CALIB_BLOCK_SIZE = 22

	def __init__(self, address=0x77, oss=3, debug=False):

		self.i2c = i2c_core(address, debug=debug)
		self.debug = debug
		
		self.calibration = self.i2c.read_block(BMP085.CALIB_BLOCK_ADDRESS, BMP085.CALIB_BLOCK_SIZE)
		self.oss = oss
		self.temp_wait_period = 0.004
		self.pressure_wait_period = 0.0255  # Conversion time
		
		# Read calibration data from sensor and store them in convenient variables
		self.ac1 = self.get_word(self.calibration, 0, True)
		self.ac2 = self.get_word(self.calibration, 2, True)
		self.ac3 = self.get_word(self.calibration, 4, True)
		self.ac4 = self.get_word(self.calibration, 6, False)
		self.ac5 = self.get_word(self.calibration, 8, False)
		self.ac6 = self.get_word(self.calibration, 10, False)
		self.b1 = self.get_word(self.calibration, 12, True)
		self.b2 = self.get_word(self.calibration, 14, True)
		self.mb = self.get_word(self.calibration, 16, True)
		self.mc = self.get_word(self.calibration, 18, True)
		self.md = self.get_word(self.calibration, 20, True)
		self.oss = self.oss

	def twos_compliment(self, val):
		if (val >= 0x8000):
		    return -((0xffff - val) + 1)
		else:
		    return val

	def get_word(self, array, index, twos):
		val = (array[index] << 8) + array[index + 1]
		if twos:
		    return self.twos_compliment(val)
		else:
		    return val        
		    
	def calculate(self):
			
		# This code is translated directly from the datasheet, I even kept the same variable names.
		# Should be very easy to understand
		
		# Read raw temperature
		self.i2c.write_8(0xF4, 0x2E)  # Tell the sensor to take a temperature reading
		time.sleep(self.temp_wait_period)  # Wait for the conversion to take place
		temp_raw = self.i2c.read_word_S16(0xF6)
		
		self.i2c.write_8(0xF4, 0x34 + (self.oss << 6))  # Tell the sensor to take a pressure reading
		time.sleep(self.pressure_wait_period)  # Wait for the conversion to take place
		pressure_raw = ((self.i2c.read_byte(0xF6) << 16) \
		             + (self.i2c.read_byte(0xF7) << 8) \
		             + (self.i2c.read_byte(0xF8))) >> (8 - self.oss)
		
		
		# Calculate temperature
		x1 = ((temp_raw - self.ac6) * self.ac5) / 32768
		x2 = (self.mc * 2048) / (x1 + self.md)
		b5 = x1 + x2
		t = (b5 + 8) / 16

		# Calculate the pressure
		b6 = b5 - 4000 
		x1 = (self.b2 * (b6 * b6 >> 12)) >> 11
		x2 = self.ac2 * b6 >> 11
		x3 = x1 + x2
		b3 = (((self.ac1 * 4 + x3) << self.oss) + 2) >> 2 
		
		x1 = (self.ac3 * b6) >> 13 
		x2 = (self.b1 * (b6 * b6 >> 12)) >> 16 
		x3 = ((x1 + x2) + 2) >> 2 
		b4 = self.ac4 * (x3 + 32768) >> 15 
		b7 = (pressure_raw - b3) * (50000 >> self.oss)
		if (b7 < 0x80000000):
		    p = (b7 * 2) / b4
		else:
		    p = (b7 / b4) * 2
		x1 = (p >> 8) * (p >> 8)
		x1 = (x1 * 3038) >> 16
		x2 = (-7357 * p) >> 16
		p = p + ((x1 + x2 + 3791) >> 4)
		
		# Calculate the altitude
		a = 0.0
		seaLevelPressure=101325
		a = 44330.0 * (1.0 - pow(p / seaLevelPressure, 0.1903))
		
		return(t / 10., p / 100., a / 100.)

	def read_pressure(self):
		(temperature, pressure) = self.calculate()
		return pressure 

	def read_temperature(self):
		(temperature, pressure) = self.calculate()
		return temperature 

	def read_temperature_and_pressure(self):
		return self.calculate()
        
if __name__ == "__main__":
	# constructor defaults : address=0x77, oss=3, debug=False
    bmp085 = BMP085()
    while True:
        print bmp085.read_temperature_and_pressure()
    


