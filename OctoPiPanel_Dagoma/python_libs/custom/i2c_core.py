#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    import smbus
except ImportError:
    raise ImportError("Error : python-smbus not found.\nInstall with 'sudo apt-get install python-smbus'")
import re

"""
================================================
ABElectronics Python Helper Functions
Version 1.1 Created 20/01/2015
Python 2 only
Requires python 2 smbus to be installed with: sudo apt-get install python-smbus
This file contains functions to load puthon smbus into an instance variable.
The bus object can then be used by multiple devices without conflicts.
================================================
"""


class i2c_core:
    
	@staticmethod
	def get_smbus():
		# detect i2C port number and assign to i2c_bus
		i2c_bus = 0
		for line in open('/proc/cpuinfo').readlines():
			m = re.match('(.*?)\s*:\s*(.*)', line)
			if m:
				(name, value) = (m.group(1), m.group(2))
				if name == "Hardware":
					if value[-4:] in ('sun7i'):
						i2c_bus = 2
						return 2
						break
				elif name == "Revision":
				    if value[-4:] in ('0002', '0003'):
				        i2c_bus = 0
				        return 0
				    else:
				        i2c_bus = 1
				        return 1
				    break
		try:        
			return smbus.SMBus(i2c_bus)
		except IOError:
			print ("Could not open the i2c bus.")
			print ("Please check that i2c is enabled and python-smbus and i2c-tools are installed.")

			result = self._bus.read_byte_data(address, reg)
			return result
		except IOError as err:
			return err
	
	def __init__(self, address, busnum=-1, debug=False):
		self.address = address
		self.bus = smbus.SMBus(busnum if busnum >= 0 else i2c_core.get_smbus())
		self.debug = debug
		if self.debug==True:
			print self.bus
    
    # Read		
	def read_byte(self, adr):
		return self.bus.read_byte_data(self.address, adr)
		
	# Read a single byte
	def read(self):
		return self.bus.read_byte(self.address)
		
	# Read a block of data
	def read_block_data(self, cmd):
		return self.bus.read_block_data(self.address, cmd)
			
	# Read a word of data
	def read_word_data(self, cmd):
		return self.bus.read_word_data(self.address, cmd)
	
	# Read a block of ranged data	
	def read_block(self, start, length):
		return self.bus.read_i2c_block_data(self.address, start, length)
		
	# Reads a unsigned 16-bit value from the I2C device #
	def read_word_U16(self, adr, little_endian=True):
		result = self.bus.read_byte_data(self.address, adr)
		if not little_endian:
			result = ((result << 8) & 0xFF00) + (result >> 8)
		return result

	# Reads a signed 16-bit value from the I2C device
	def read_word_S16(self, adr, little_endian=True):		
		val = self.read_word_U16(adr,little_endian)
		if (val >= 32768):
			return -((65535 - val) + 1)
		else:
			return val
			
	def read_word(self, reg):
		high = self.read_byte(reg)
		low = self.read_byte(reg+1)
		val = (high << 8) + low
		return val

	def read_word_2c(self, reg):
		val = self.read_word(reg)
		if (val >= 0x8000):
			return -((65535 - val) + 1)
		else:
			return val

	# Write a single command
	def write_cmd(self, cmd):
		self.bus.write_byte(self.address, cmd)

	# Writes an 8-bit value to the specified register/address		
	def write_8(self, reg, value):		
		self.bus.write_byte_data(self.address, reg, value)
	
	# Writes a 16-bit value to the specified register/address pair	
	def write_16(self, reg, value):
		self.bus.write_word_data(self.address, reg, value)
		
	# Write a block of data
	def write_block_data(self, cmd, data):
		self.bus.write_block_data(self.address, cmd, data)
	
	# Writes an array of bytes using I2C format	
	def writeList(self, reg, list):
		self.bus.write_i2c_block_data(self.address, reg, list)
	
