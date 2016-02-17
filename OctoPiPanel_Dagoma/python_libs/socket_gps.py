#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Connects to an open socket, and grabs position data
# Usually works with an android device server and a custom app
# Parses this data format :
# 		data				type
# <compass>xxx</compass>	degrees
# <pitch>xxx</pitch>		degrees
# <roll>xxx</roll>			degrees
# <lat>xxx</lat>			latitude
# <lon>xxx</lon> 			longitude
# <alt>xxx</alt> 			altitude (m)
# <speed>xxx</speed> 		speed (km/h)
# <acc>xxx</acc> 			gps accuracy (m)
# <sats>xxx</sats>			satellites in use (number) 
     
import socket
import os
import sys
import time
import threading

class GPS():
	def __init__(self, ip="192.168.1.63", port=5001, delay=0.2):
	
		self.ip = ip
		self.port = port
		self.delay = delay
		
		self.compass = None
		self.pitch = None
		self.roll = None
		self.lat = None
		self.lon = None
		self.alt = None
		self.speed = None
		self.acc = None
		self.sats = None
		self.data = None
		
		self.running = False
	
	def start_gps(self):
		#creation du socket puis connexion
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect()
		
	def connect(self):
		try:
			self.socket.connect((self.ip, self.port))

			# preparation de la requete
			self.Request = "GET / HTTP/1.1\r\n"
			 
			# envoi puis reception de la reponse
			self.socket.send(self.Request)
	
			# démarrage de la boucle
			self.running = True
			self.get_gps()
		except:
			self.data = "None"
			self.stop_gps()
			t = threading.Timer(2, self.start_gps)
			t.start()				
		
	def stop_gps(self):
		self.running = False
		self.socket.close()
		
	def get_gps(self):
		rcvdata = None
		try:
			rcvdata = self.socket.recv(512)
		except:
			self.running = False
			self.data = None
			self.stop_gps()
			self.connect()

		if rcvdata:
			for w in rcvdata.split("</compass>"):
				if "<compass>" in w:
					compass = w.split('<compass>')[-1:]
					compass = str(compass).replace("['", "")
					self.compass = str(compass).replace("']", "")
		
			for w in rcvdata.split("</pitch>"):
				if "<pitch>" in w:
					pitch = w.split('<pitch>')[-1:]
					pitch = str(pitch).replace("['", "")
					self.pitch = str(pitch).replace("']", "")
		
			for w in rcvdata.split("</roll>"):
				if "<roll>" in w:
					roll = w.split('<roll>')[-1:]
					roll = str(roll).replace("['", "")
					self.roll = str(roll).replace("']", "")
		
			for w in rcvdata.split("</lat>"):
				if "<lat>" in w:
					lat = w.split('<lat>')[-1:]
					lat = str(lat).replace("['", "")
					self.lat = str(lat).replace("']", "")
		
			for w in rcvdata.split("</lon>"):
				if "<lon>" in w:
					lon = w.split('<lon>')[-1:]
					lon = str(lon).replace("['", "")
					self.lon = str(lon).replace("']", "")
		
			for w in rcvdata.split("</alt>"):
				if "<alt>" in w:
					alt = w.split('<alt>')[-1:]
					alt = str(alt).replace("['", "")
					self.alt = str(alt).replace("']", "")
		
			for w in rcvdata.split("</speed>"):
				if "<speed>" in w:
					speed = w.split('<speed>')[-1:]
					speed = str(speed).replace("['", "")
					self.speed = str(speed).replace("']", "")
		
			for w in rcvdata.split("</acc>"):
				if "<acc>" in w:
					acc = w.split('<acc>')[-1:]
					acc = str(acc).replace("['", "")
					self.acc = str(acc).replace("']", "")
		
			for w in rcvdata.split("</sats>"):
				if "<sats>" in w:
					sats = w.split('<sats>')[-1:]
					sats = str(sats).replace("['", "")
					self.sats = str(sats).replace("']", "")

			self.data = (self.compass, 
					self.pitch, 
					self.roll, 
					self.lat, 
					self.lon, 
					self.alt, 
					self.speed,
					self.acc, 
					self.sats)
		
		if self.running == True:
			t = threading.Timer(self.delay, self.get_gps)
			t.start()

if __name__ == "__main__":
	gps = GPS()
	gps.start_gps()
	running = True
	while running == True:
		try:
#			os.system('clear')
			print gps.data
			time.sleep(0.1)
		except KeyboardInterrupt:
			gps.stop_gps()
			running = False
	sys.exit()
