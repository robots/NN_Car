#!/usr/bin/python

import cv
import pygame
import math
import numpy
import sys
import time
import gzip
import pickle

from serial_car import SerialCar

def gen_palette_fire():
	gstep, bstep = 75, 150
	cmap = numpy.zeros((256, 3))
	cmap[:,0] = numpy.minimum(numpy.arange(256)*3, 255)
	cmap[gstep:,1] = cmap[:-gstep,0]
	cmap[bstep:,2] = cmap[:-bstep,0]
	return cmap

def gen_palette_gray():
	return [(x, x, x) for x in range(256)]

def frame2surface(frame):
	frame_rgb = cv.CreateMat(frame.height, frame.width, cv.CV_8UC3)
	cv.CvtColor(frame, frame_rgb, cv.CV_BGR2RGB)

	return pygame.image.frombuffer(frame_rgb.tostring(), cv.GetSize(frame_rgb), "RGB")

def frame2gray(frame):
	frame_gray = cv.CreateMat(frame.height, frame.width, cv.CV_8UC1)
	cv.CvtColor(frame, frame_gray, cv.CV_BGR2GRAY)

	return frame_gray

def expo(x, p = 5):
	return (x*x*x / (p-1) + x ) / p;

def drawframe(frame, velx, vely):
	srfc = pygame.image.frombuffer(frame.tostring(), cv.GetSize(frame), "P")
	srfc.set_palette(palette)
	screen.blit(srfc, (0, 0))

	for x in range(res_work[0]):
		for y in range(res_work[1]):
			valx = (cv.Get2D(velx, y, x)[0] * scale)
			valy = (cv.Get2D(vely, y, x)[0] * scale)

			basex = x * scale + scale/2
			basey = y * scale + scale/2
#			print res_work[0], res_work[1], valx, x, y

			pygame.draw.line(screen, red, (basex, basey), (round(basex+valx), round(basey+valy)))

	pygame.display.flip()


def img2ary(img):
	a = numpy.fromstring(img.tostring(), numpy.float32)
	a.shape = cv.GetSize(img)
	return a


def handle_events():
	global window, output_file, writer

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit(0)
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				window = window + 2
				print window
			elif event.key == pygame.K_DOWN:
				window = window - 2
				print window
			elif event.key == pygame.K_ESCAPE:
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
				sys.exit(0)

			


pygame.init()

red = pygame.Color("red")

cap = cv.CaptureFromCAM(-1)

#overkillllll
#cv.SetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_WIDTH, 1024);
#cv.SetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_HEIGHT, 768);

frame_raw = cv.QueryFrame(cap)

res_input = cv.GetSize(frame_raw)
scale = 32
window = 9
res_work = (res_input[0] / scale, res_input[1] / scale)

screen = pygame.display.set_mode(res_input)
#alette = gen_palette_fire()
palette = gen_palette_gray()
pygame.display.set_caption("test")

joystick = pygame.joystick.Joystick(0)
joystick.init()

robot = SerialCar('/dev/ttyUSB0', 38400)
out_values = [0, 0]

velx = cv.CreateImage(res_work, cv.IPL_DEPTH_32F, 1)
vely = cv.CreateImage(res_work, cv.IPL_DEPTH_32F, 1)

frame_new = cv.CreateImage(res_work, cv.IPL_DEPTH_8U, 1)
frame_old = cv.CreateImage(res_work, cv.IPL_DEPTH_8U, 1)

output_file = open("/dev/null", "w")
#output_file = gzip.open("data_" + time.strftime("%Y%m%d_%H%M%S"), "w")

#fourcc = cv.CV_FOURCC('I','4','2','0')
#writer = cv.CreateVideoWriter('/dev/null', fourcc, 16, res_input, 1)

try:
	while True:
		frame_raw = cv.QueryFrame(cap)
		#cv.WriteFrame(writer, frame_raw)

		frame_gray = frame2gray(frame_raw)

		frame_old, frame_new = frame_new, frame_old
		cv.Resize(frame_gray, frame_new);

		cv.CalcOpticalFlowLK(frame_old, frame_new, (window, window), velx, vely)

		drawframe(frame_gray, velx, vely)

		handle_events()
		robot.set_speed(out_values[0], out_values[1])

		pickle.dump((img2ary(velx), img2ary(vely), out_values, time.time()), output_file)
#		print "Speed: {} forward, {} turn".format(out_values[0], out_values[1])

except KeyboardInterrupt:
	print "Terminated..."
    

