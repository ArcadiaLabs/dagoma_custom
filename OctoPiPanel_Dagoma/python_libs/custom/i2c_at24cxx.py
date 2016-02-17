#!/usr/bin/python
# -*- coding: utf-8 -*-
# ==================================================
# ATMEL AT24C16 16kb I2C EEPROM and AT24CXX series
# Datasheet:  http://www.atmel.com/Images/doc3256.pdf
# ==================================================
#          _____
#	A0	- 1	\_/	8 - VCC
#	A1	- 2		7 - WP
#	A2  - 3		6 - SCL	
#	GND	- 4_____5 - SDA
#
# Note : chip uses several I2C addresses, one per bank
# on AT24C16, one bank is 128 pages of 16 bytes each. See datasheet for others.
# Actually this lib could only contruct 1 object / bank (= 1 object / address)
# ==================================================

import time
from i2c_core import i2c_core

class AT24CXX(object):
	
	def __init__(self, address=0x50, debug=False):
		self.debug = debug
		self.address = address
		self.i2c = i2c_core(self.address, debug=debug)	
	
	def eeprom_read(self, block):
		return self.i2c.read_word_S16(block)
		
	def eeprom_write(self, block, data):
		self.i2c.write_16(block, data)
		

if __name__ == "__main__":
	# constructor defaults : address=0x50, debug=False
	i2c_AT24C16 = AT24CXX(address=0x50, debug=False)
	i = 0
	print 'write'
	while i < 256:
		print hex(i), i
		i2c_AT24C16.eeprom_write(i, i)
		time.sleep(0.01)
		i+=1
	
	i = 0
	print '\nread'	
	while i < 256:
		print hex(i), i2c_AT24C16.eeprom_read(i)
		i+=1
	
