#!/usr/bin/python

import pygame
import math
import sys
import gzip
import pickle
import time

from serial_car import SerialCar
from vision import Vision

def handle_events():
	global window, output_file, writer

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit(0)
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				sys.exit(0)
		elif event.type == pygame.JOYAXISMOTION:
			if event.axis == 0:
				out_values[1] = event.value
			elif event.axis == 1:
				out_values[0] = -event.value
		elif event.type == pygame.JOYBUTTONUP:
			if event.button == 3:
				filename = "data_" + time.strftime("%Y%m%d_%H%M%S")
				print "Starting recording to file" + filename
				output_file.close()
				output_file = gzip.open(filename+".gz", "w")
				#writer = cv.CreateVideoWriter(filename+".avi", fourcc, 16, res_input, 1)
			elif event.button == 2:
				output_file.close()
				output_file = open("/dev/null", "w")
				#writer = cv.CreateVideoWriter('/dev/null', fourcc, 16, res_input, 1)
			elif event.button == 8:
				robot.set_speed(0, 0)
				sys.exit(0)

pygame.init()

vision = Vision("Record")

joystick = pygame.joystick.Joystick(0)
joystick.init()

robot = SerialCar('/dev/ttyUSB0', 38400)
out_values = [0, 0]

output_file = open("/dev/null", "w")

try:
	while True:
		
		handle_events()

		robot.set_speed(out_values[0], out_values[1])

		in_values = vision.frame()

		pickle.dump((in_values, out_values), output_file)

#		print "Speed: {} forward, {} turn".format(out_values[0], out_values[1])

except KeyboardInterrupt:
	print "Terminated..."
    

