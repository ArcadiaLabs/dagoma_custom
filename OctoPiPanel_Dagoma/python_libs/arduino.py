#! /usr/bin/env python
# -*- coding: utf-8 -*-

# --- arduino - serial ---
import serial
import time

def get_uart_device(locations, debug = False):

	for device in locations: 
		if debug:
			print "udp2uart : Trying...",device
		try:
			arduino = serial.Serial(device, 9600, timeout=2, bytesize=8, parity='N', stopbits=1)
			try:
				arduino.write("42/")
				#time.sleep(0.1)
				answer = format(arduino.readline().strip('\r\n').strip())
				var_type = type(answer)
				#print(var_type)
				if ("arduino" in answer):
					arduino.close()
					arduino.open()
					found_device = device
					if debug:
						print("Arduino trouvé sur  "+device+"")
					break
				else:
					print("mauvaise réponse de "+device+" ("+answer+")")
			except:
				found_device = False
				if debug:
					print("udp2uart : echec de l'envoi des données à "+device+"")
		except:
			found_device = False
			if debug:
				print("udp2uart : echec de la connexion à "+device+"")
	return found_device
