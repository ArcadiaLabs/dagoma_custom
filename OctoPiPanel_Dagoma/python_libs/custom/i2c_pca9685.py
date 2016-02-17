#!/usr/bin/python
# -*- coding: utf-8 -*-
# ==================================================
# NXP PCA9685 16 Channels PMW controller
# Datasheet : http://www.nxp.com/documents/data_sheet/PCA9685.pdf
# ==================================================
#
# For use with breakout boards like : 
# http://www.adafruit.com/products/815
# http://shop.mchobby.be/breakout/89-adafruit-controleur-pwm-servo-16-canaux-12-bits-i2c-interface-pca9685-3232100000896.html
# ==================================================

import time
import math
import re
import RPi.GPIO as GPIO
from i2c_core import i2c_core

class PCA9685(object):

	# Define registers values from datasheet
	MODE1 = 0x00
	MODE2 = 0x01
	SUBADR1 = 0x02
	SUBADR2 = 0x03
	SUBADR3 = 0x04
	ALLCALLADR = 0x05
	LED0_ON_L = 0x06
	LED0_ON_H = 0x07
	LED0_OFF_L = 0x08
	LED0_OFF_H = 0x09
	ALL_LED_ON_L = 0xFA
	ALL_LED_ON_H = 0xFB
	ALL_LED_OFF_L = 0xFC
	ALL_LED_OFF_H = 0xFD
	PRE_SCALE = 0xFE

	def __init__(self, address=0x40, oepin=18, debug=False, servoMin=150, servoMax=500):
		self.debug = debug
		self.address = address
		self.oepin = oepin
		self.servoMin=servoMin
		self.servoMax=servoMax
		self.i2c = i2c_core(address, debug=debug)
		self.i2c.write_8(self.MODE1, 0x00)

	def set_pwm_freq(self, freq):
		# Set the PWM frequency #

		scaleval = 25000000.0    # 25MHz (PCA9685 internal oscillator value)
		scaleval /= 4096.0       # 12-bit (PCA9685 resolution)
		scaleval /= float(freq)
		scaleval -= 1.0
		prescale = math.floor(scaleval + 0.5)
		oldmode = self.i2c.read_byte(self.MODE1)
		newmode = (oldmode & 0x7F) | 0x10
		self.i2c.write_8(self.MODE1, newmode)
		self.i2c.write_8(self.PRE_SCALE, int(math.floor(prescale)))
		self.i2c.write_8(self.MODE1, oldmode)
		time.sleep(0.005)
		self.i2c.write_8(self.MODE1, oldmode | 0x80)

	def set_pwm(self, channel, on, off):
		# set the output on a single channel #

		self.i2c.write_8(self.LED0_ON_L + 4 * channel, on & 0xFF)
		self.i2c.write_8(self.LED0_ON_H + 4 * channel, on >> 8)
		self.i2c.write_8(self.LED0_OFF_L + 4 * channel, off & 0xFF)
		self.i2c.write_8(self.LED0_OFF_H + 4 * channel, off >> 8)

	def set_all_pwm(self, on, off):
		# set the output on all channels #

		self.i2c.write_8(self.ALL_LED_ON_L, on & 0xFF)
		self.i2c.write_8(self.ALL_LED_ON_H, on >> 8)
		self.i2c.write_8(self.ALL_LED_OFF_L, off & 0xFF)
		self.i2c.write_8(self.ALL_LED_OFF_H, off >> 8)
	
	def arduino_map(self, x, in_min, in_max, out_min, out_max):
		return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
		
	def servo_move(self, servo, position):
		pulse = self.arduino_map(int(position), 0, 180, int(self.servoMin), int(self.servoMax))
		self.set_pwm(int(servo), 0, int(pulse))
		
	def oe_init(self, oepin):
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(oepin, GPIO.OUT)
		self.output_enable()

	def output_disable(self):
		# disable output via OE pin #
		GPIO.output(self.oepin, True)

	def output_enable(self):
		# enable output via OE pin #
		GPIO.output(self.oepin, False)

if __name__ == "__main__":

	# set the servo minimum, centre and maximum limits
	servoMin = 150  # Min pulse length out of 4096
	servoMax = 500  # Max pulse length out of 4096
	
	# constructor defaults : address=0x40, oepin=18, debug=False, servoMin=150, servoMax=500
	i2c_pwm = PCA9685(servoMin=servoMin, servoMax=servoMax)
	i2c_pwm.set_pwm_freq(60)

	while True:
		# servo_move(servo #, position (0-180), 
		i2c_pwm.servo_move(4, 0)
		time.sleep(1)
		i2c_pwm.servo_move(4, 90)
		time.sleep(1)
		i2c_pwm.servo_move(4, 180)
		time.sleep(1)
		i2c_pwm.servo_move(4, 90)
		time.sleep(1)
