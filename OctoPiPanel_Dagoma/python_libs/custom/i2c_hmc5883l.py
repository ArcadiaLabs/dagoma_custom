#!/usr/bin/python
# -*- coding: utf-8 -*-
# ==================================================
# Honeywell HMC5883L Magnetometer
# Datasheet : http://www51.honeywell.com/aero/common/documents/myaerospacecatalog-documents/Defense_Brochures-documents/HMC5883L_3-Axis_Digital_Compass_IC.pdf
# ==================================================
#
# Adapted from: http://think-bowl.com/raspberry-pi/i2c-python-library-3-axis-digital-compass-HMC58835883l-with-the-raspberry-pi/ for my own i2c core library
# ==================================================
#
# Breakout board known as GY-271
# ==================================================

import math
from i2c_core import i2c_core


class HMC5883(object):

	# Define registers values from datasheet
    ConfigurationRegisterA = 0x00
    ConfigurationRegisterB = 0x01
    ModeRegister = 0x02

    AxisXDataRegisterMSB = 0x03
    AxisXDataRegisterLSB = 0x04
    AxisZDataRegisterMSB = 0x05
    AxisZDataRegisterLSB = 0x06
    AxisYDataRegisterMSB = 0x07
    AxisYDataRegisterLSB = 0x08

    StatusRegister = 0x09
    IdentificationRegisterA = 0x10
    IdentificationRegisterB = 0x11
    IdentificationRegisterC = 0x12

    MeasurementContinuous = 0x00
    MeasurementSingleShot = 0x01
    MeasurementIdle = 0x03

    def __init__(self, address=0x1e, busnum=-1, gauss=1.3, debug=False):
    	self.debug = debug
        self.i2c = i2c_core(address, busnum=busnum, debug=debug,)
        self.i2c.write_8(self.ConfigurationRegisterA, 0b01110000) # Set to 8 samples @ 15Hz		
        self.set_scale(gauss, debug=debug)
        self.set_continuous_mode() # Continuous sampling
        

#	def read_word(self, reg):
#		high = self.i2c.read_byte(address, reg)
#		low = self.i2c.read_byte(address, reg+1)
#		val = (high << 8) + low
#		return val

#	def read_word_2c(self, reg):
#		val = read_word(reg)
#		if (val >= 0x8000):
#			return -((65535 - val) + 1)
#		else:
#			return val
			
    def set_scale(self, gauss, debug=False):
        if gauss == 0.88:
            self.scale_reg = 0x00
            self.scale = 0.73
        elif gauss == 1.3:
            self.scale_reg = 0x01
            self.scale = 0.92
        elif gauss == 1.9:
            self.scale_reg = 0x02
            self.scale = 1.22
        elif gauss == 2.5:
            self.scale_reg = 0x03
            self.scale = 1.52
        elif gauss == 4.0:
            self.scale_reg = 0x04
            self.scale = 2.27
        elif gauss == 4.7:
            self.scale_reg = 0x05
            self.scale = 2.56
        elif gauss == 5.6:
            self.scale_reg = 0x06
            self.scale = 3.03
        elif gauss == 8.1:
            self.scale_reg = 0x07
            self.scale = 4.35

		
        self.scale_reg = self.scale_reg << 5
        self.set_option(self.ConfigurationRegisterB, self.scale_reg)
        if debug == True:
        	print("HMC5883L set : gauss "+gauss+", scale "+scale)

    def set_option(self, register, *function_set):
        options = 0x00
        for function in function_set:
            options = options | function
        self.i2c.write_8(register, options)

    def get_axes(self):
        magno_x = self.i2c.read_word_2c(self.AxisXDataRegisterMSB)
        magno_y = self.i2c.read_word_2c(self.AxisYDataRegisterMSB)
        magno_z = self.i2c.read_word_2c(self.AxisZDataRegisterMSB)

        if (magno_x == -4096):
            magno_x = None
        else:
            magno_x = round(magno_x * self.scale, 4)

        if (magno_y == -4096):
            magno_y = None
        else:
            magno_y = round(magno_y * self.scale, 4)

        if (magno_z == -4096):
            magno_z = None
        else:
            magno_z = round(magno_z * self.scale, 4)

        return (magno_x, magno_y, magno_z)

    def get_heading(self):
        (scaled_x, scaled_y, scaled_z) = self.get_axes()

        heading_rad = math.atan2(scaled_y, scaled_x)
        heading_rad += self.declination

        # Correct for reversed heading
        if(heading_rad < 0):
            heading_rad += 2 * math.pi

        # Check for wrap and compensate
        if(heading_rad > 2 * math.pi):
            heading_rad -= 2 * math.pi

        # Convert to degrees from radians
        heading_deg = heading_rad * 180 / math.pi
        degrees = math.floor(heading_deg)
        minutes = round(((heading_deg - degrees) * 60))
        return (degrees, minutes)

    def set_declination(self, degree, min=0):
        self.declinationDeg = degree
        self.declinationMin = min
        self.declination = (degree + min / 60) * (math.pi / 180)

    def __str__(self):
        ret_str = ""
        (x, y, z) = self.get_axes()
        ret_str += "Axis X: " + str(x) + "\n"
        ret_str += "Axis Y: " + str(y) + "\n"
        ret_str += "Axis Z: " + str(z) + "\n"

        ret_str += "Declination: " + self.get_declination_string() + "\n"

        ret_str += "Heading: " + self.get_heading_string() + "\n"

        return ret_str

    def get_declination_string(self):
        return str(self.declinationDeg) + " deg, " + str(self.declinationMin) + " minutes"

    def get_heading_string(self):
        (degrees, minutes) = self.get_heading()
        return str(degrees) + " deg, " + str(minutes) + " minutes"

    def set_continuous_mode(self):
        self.set_option(self.ModeRegister, self.MeasurementContinuous)
        
if __name__ == "__main__":
	# constructor defaults : address=0x1e, gauss=1.3, debug=False
	i2c_HMC5883l = HMC5883(gauss=1.3)
	i2c_HMC5883l.set_declination(2, 18)
	while True:
		print i2c_HMC5883l.get_heading()
