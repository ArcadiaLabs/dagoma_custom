#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import pygame.camera
from pygame.locals import *
import time
import threading

pygame.camera.init()

class CameraCapture():
	def __init__(self, device, resolution, captureframerate=30):
		# check cameras
		self.clist = pygame.camera.list_cameras()
		if not self.clist:
			raise ValueError("Sorry, no cameras detected.")
			
		# Initialize the selected camera
		self.camera = pygame.camera.Camera(self.clist[device], resolution)
		self.camera.start()

		# Set up a camera surface, won't be used directly for display
		self.camera_surface = pygame.Surface(resolution)
		self.period = 1/float(captureframerate)
		self.stop = True
		
		# prepare camera framerate clock
		self.camclock = pygame.time.Clock()
		self.cam_fps = 0
		self.captureclock = pygame.time.Clock()
		self.capture_fps = 0
		
		# fill the camera surface with a first image
		self.camera_surface = self.camera.get_image()
		# create a surface for displaying and copy the first image in it
		self.camera_image = self.camera_surface
	
	def stop_camera(self):
		self.camera.stop()
		
	def stop_capture(self):
		self.stop = True
		self.stop_camera(self)
	
	def start_capture(self):
		if self.stop == True:
			self.stop = False
			self.capture_image()
			
	def capture_image(self):
		# Time start
		time_start = time.time()

		# update camera capture clock
		self.captureclock.tick()
		self.capture_fps = self.captureclock.get_fps()		
	
		# If image ready, get it and update camera fps clock
#		if self.camera.query_image():
#			self.camera_surface = self.camera.get_image()
#			self.camclock.tick()
#			self.cam_fps = self.camclock.get_fps()	
		
		self.camera_surface = self.camera.get_image()
			
		# make a copy of the existing surface
		self.camera_image = self.camera_surface
		
		#If not stopped, prepare for the next capture
		if self.stop == False:
			time_elapsed = time.time() - time_start
			if time_elapsed >= self.period:
				time_wait = 0
			else:
				time_wait = self.period - time_elapsed
#			pygame.time.wait(int(time_wait))
			t = threading.Timer(time_wait, self.capture_image)
			t.start()
