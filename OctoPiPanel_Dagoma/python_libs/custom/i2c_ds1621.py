#!/usr/bin/python
# -*- coding: utf-8 -*-
# ==================================================
# Maxim DS1621 I2C Temperature sensor
# Low accuracy (0.5°C)
# Datasheet:  http://pdfserv.maximintegrated.com/en/ds/DS1621.pdf
# ==================================================
#          _____
#	SDA	- 1	\_/	8 - Vdd
#	SCL	- 2		7 - A0
#	Tout- 3		6 - A1	
#	GND	- 4_____5 - A2
#
# Default address : 0x48 (A0, A1, A2 to GND)
# ==================================================

from i2c_core import i2c_core

class DS1621(object):

	FREQ = 100000
	ADDRESS_SIZE = 7

	# Define registers values from datasheet
	REG_READ_TEMP 		= 0xAA
	REG_READ_COUNTER 	= 0xA8
	REG_READ_SLOPE 		= 0xA9
	REG_ACCESS_CONFIG   = 0xAC
	REG_ACCESS_TH       = 0xA1
	REG_ACCESS_TL       = 0xA2
	REG_START_CONV = 0xEE
	REG_STOP_CONV = 0x22

	# read-only status bits
	DONE      = 0x80
	TH_BIT    = 0x40
	TL_BIT    = 0x20
	NVB       = 0x10 # Non-Volatile memory Busy

	# r/w status bits (bit masks)
	POL_HI    = 0x02
	POL_LO    = 0xFD
	ONE_SHOT  = 0x01
	CONT_MODE = 0xFE
	CLR_TL_TH = 0x9F
	

	def __init__(self, address=0x48, debug=False):
		self.debug = debug
		self.address = address
		self.i2c = i2c_core(self.address, debug=debug)
		self.i2c.write_8(self.REG_ACCESS_CONFIG, 0x00)
		self.i2c.write_cmd(self.REG_START_CONV)
		
	def twos_comp(self, byte):
		# input byte in two's complement is returned as signed integer
		if len(bin(byte)[2:]) > 8:
			# shouldn't ever get here
			print '\nWarning: input '+str(hex(byte))+' truncated to least significant byte : '+str(hex(0xFF & byte))
		byte = 0xFF & byte
		return ~(255 - byte) if byte > 127 else byte
	
	def decode_DS(self, word):
		# 2-byte data from DS1621 is received as LSB MSB
		# MSB is a two's complement number from -55 to +125
		# If leftmost bit from LSB is set, add .5 to reading. 
		LSB = word // 256 # integer division with two // because we're using division from Python 3
		MSB = word % 256
		value = self.twos_comp(MSB)
		return value + .5 if LSB == 128 else value + .0
	
	def encode_DS(self, num):
		# 2-byte thermostat setting sent to DS1621
		# in same format as data received, see decode_DS, above.
		
		# warn for out of range and set within range.
		if num < -55:
			print '\nWarning: input ' + str(num) + ' out of range, set to -55'
			num = -55
		if num > 125:
			print '\nWarning: input ' + str(num) + ' out of range, set to 125'
			num = 125
		# round off to nearest .5
		num = round(num*2)/2.0
		MSB = int(num)
		decimal = num - MSB
		# LSB is binary 1000.0000 if decimal = .5, otherwise 0
		# data is sent LSB MSB
		if decimal == 0:
			return MSB
		else:
			if MSB > 0:
				return MSB | 0x8000
			else:
				return (MSB - 1) & 0x80FF 
	
	def read_temp(self):
		v=self.i2c.read_byte(self.REG_READ_TEMP)
		if v > 127:
			v -= 256
		return v
		
	def read_degrees(self):
		DegreesC_byte = self.twos_comp(self.i2c.read_byte(self.REG_READ_TEMP))
		DegreesC_word = self.decode_DS(self.i2c.read_word_data(self.REG_READ_TEMP))
		Slope = self.i2c.read_byte(self.REG_READ_SLOPE)
		Counter = self.i2c.read_byte(self.REG_READ_COUNTER)
		DegreesC_HR = DegreesC_byte - .25 + (Slope - Counter)/Slope
		return DegreesC_byte, DegreesC_word, DegreesC_HR
	
	# returns temperature as high-res value, as per DS1621 datasheet
	def read_degreesC_hiRes(self):
		DegreesC_byte = self.twos_comp(self.i2c.read_byte(self.REG_READ_TEMP))
		Slope = self.i2c.read_byte(self.REG_READ_SLOPE)
		Counter = self.i2c.read_byte(self.REG_READ_COUNTER)
		DegreesC_HR = DegreesC_byte - .25 + (Slope - Counter)/Slope
		return DegreesC_HR
		
	def read_config(self):
		Conf = self.i2c.read_byte(self.REG_ACCESS_CONFIG)

		TH = self.decode_DS(self.i2c.read_word_U16(self.REG_ACCESS_TH))
		TL = self.decode_DS(self.i2c.read_word_U16(self.REG_ACCESS_TL))
		
		if Conf & self.POL_HI:
			level, device = 'HIGH', 'cooler' 
		else: 
			level, device = 'LOW', 'heater'  

		Rpt = '''\nStatus of DS1621 at address {sensor}:
\tConversion is {convstat}
\t{have_th} measured {th} degrees Celsius or more
\t{have_tl} measured below {tl} degrees Celsius
\tNon-volatile memory is {busy}
\tThermostat output is Active {level} (1 turns the {device} on)
\tMeasuring mode is {mode}'''

		print Rpt.format(
				sensor = hex(self.address),
				convstat = 'done' if Conf & self.DONE else 'in process',
				have_th = 'HAVE' if Conf & self.TH_BIT else 'have NOT', 
				th = TH, 
				have_tl = 'HAVE' if Conf & self.TL_BIT else 'have NOT', 
				tl = TL,
				busy = 'BUSY' if Conf & self.NVB else 'not busy',
				level = level, 
				device = device,
				mode = 'One-Shot' if Conf & self.ONE_SHOT else 'Continuous', 
				)
		     
		return Conf, TH, TL
	
	# returns low and high thermostat settings
	def get_thermostat(self):	
		low_therm = self.decode_DS(self.i2c.read_word_U16(self.REG_ACCESS_TL))
		hi_therm = self.decode_DS(self.i2c.read_word_U16(self.REG_ACCESS_TH))
		return low_therm, hi_therm
	
	def wait_NVM(self):
		newConf = self.i2c.read_byte(self.REG_ACCESS_CONFIG)
		# wait for write to Non-Volatile Memory to finish 
		while newConf & self.NVB: 
			newConf = self.i2c.read_byte(self.REG_ACCESS_CONFIG)
		return 
    	
	def write_conf_byte(self, byte): 
		self.i2c.write_8(self.REG_ACCESS_CONFIG, byte)
		self.wait_NVM()
		return 
		
	# sets new lower and upper thermostat limits for thermostat pin
	# in non-volatile memory; also reset TH and TH bits. 
	def set_thermostat(self, lower, upper):
		self.i2c.write_16(self.REG_ACCESS_TL, self.encode_DS(lower))
		self.i2c.write_16(self.REG_ACCESS_TH, self.encode_DS(upper))
		self.wait_NVM()
		
		Conf = self.i2c.read_byte_data(self.REG_ACCESS_CONFIG) & self.CLR_TL_TH
		self.write_conf_byte(Conf)
		return
	
	# Sets upper temp with hysteresis for thermostat pin
    # and reset TH and TH bits.
	def set_thermohyst(self, upper, hyst=0.5):  
		set_thermostat(upper - hyst, upper)
		return
		
	def set_1shot(self):
		Conf = self.i2c.read_byte(self.REG_ACCESS_CONFIG) | self.ONE_SHOT
		self.write_conf_byte(Conf)
		return
    
	def set_continuous(self):
		Conf = self.i2c.read_byte(self.REG_ACCESS_CONFIG) & self.CONT_MODE
		self.write_conf_byte(Conf)
		return

	def set_thermoLOW(self, LOW=True): 
		Conf = self.i2c.read_byte(self.REG_ACCESS_CONFIG)
		Conf = Conf & self.POL_LO if LOW else Conf | self.POL_HI  
		self.write_conf_byte(Conf)
		return

if __name__ == "__main__":
	# constructor defaults : address=0x48, debug=False
	i2c_DS1621 = DS1621(address=0x48)
	# reads config
	i2c_DS1621.read_config()
	print "thermostat limits : "+str(i2c_DS1621.get_thermostat())
	
	# sets measure mode. should be set to continuous for normal operation (default)
#	i2c_DS1621.set_1shot()
#	i2c_DS1621.set_continuous()

	# sets new lower and upper thermostat limits for thermostat pin
#	i2c_DS1621.set_thermostat(lower, higher)
	# sets upper temp with hysteresis for thermostat pin
#	i2c_DS1621.set_thermohyst(self, upper, hyst=0.5)

#	print "temperature : "+str(i2c_DS1621.read_temp())
	print "degrees (int, float, HR) : "+str(i2c_DS1621.read_degrees())
	
