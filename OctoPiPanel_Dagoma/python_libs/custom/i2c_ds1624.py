#!/usr/bin/python
# -*- coding: utf-8 -*-
# ==================================================
# Maxim DS1624 I2C Temperature sensor + 256b eeprom
# High accuracy (0.03°C)
# Datasheet:  http://datasheets.maximintegrated.com/en/ds/DS1624.pdf
# ==================================================
#          _____
#	SDA	- 1	\_/	8 - Vdd
#	SCL	- 2		7 - A0
#	NC  - 3		6 - A1	
#	GND	- 4_____5 - A2
#
# Default address : 0x48 (A0, A1, A2 to GND)
# ==================================================

import time
from i2c_core import i2c_core

class DS1624(object):

	# Define registers values from datasheet
	REG_ACCESS_CONFIG   = 0xAC	
	REG_READ_TEMP		= 0xAA
	REG_READ_MEM		= 0x17
	START 				= 0xEE
	
	CONTINUOUS_MODE 			= 0x00
	
	def __init__(self, address=0x48, debug=False):
		self.debug = debug
		self.address = address
		self.i2c = i2c_core(self.address, debug=debug)
		self.i2c.write_8(self.REG_ACCESS_CONFIG, self.CONTINUOUS_MODE)
		time.sleep(0.1)
		self.i2c.write_cmd(self.START)		
	
	def read_temp(self):
		temp1 = self.i2c.read_word_data(self.REG_READ_TEMP)
		temp_l = (temp1 & 0xFF00) >> 8
		temp_h = temp1 & 0x00FF
		temp_l = temp_l >> 3
		if (temp_h & 0x80) == 0x80:
			temp_l = (~temp_l) + 1
		return temp_h + ( 0.03125 * temp_l)
		

if __name__ == "__main__":
	# constructor defaults : address=0x48, debug=False
	i2c_DS1624 = DS1624(address=0x48)
	while True:
		print "degrees (float) : "+str(i2c_DS1624.read_temp())
	
