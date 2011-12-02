#!/usr/bin/python

import pygame
import math
import sys
import gzip
import pickle
from pyfann import libfann

from serial_car import SerialCar
from vision import Vision

def handle_events():
	global window, pause

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			robot.set_speed(0, 0)
			sys.exit(0)
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				robot.set_speed(0, 0)
				sys.exit(0)
		elif event.type == pygame.JOYBUTTONUP:
			if event.button == 8:
				robot.set_speed(0, 0)
				sys.exit(0)
			elif event.button == 1:
				pause = not pause



pygame.init()

pause = False
vision = Vision("Driver")

joystick = pygame.joystick.Joystick(0)
joystick.init()

robot = SerialCar('/dev/ttyUSB0', 38400)
out_values = [0, 0]

nn = libfann.neural_net()
nn.create_from_file(sys.argv[1])

try:
	while True:
		
		handle_events()

		in_values = vision.frame()

		out_values = nn.run(in_values)

		if pause:
			robot.set_speed(0, 0)
		else:
			robot.set_speed(out_values[0], out_values[1])

		print "Speed: {} forward, {} turn".format(out_values[0], out_values[1])

except KeyboardInterrupt:
	print "Terminated..."
    

robot.set_speed(0, 0)
