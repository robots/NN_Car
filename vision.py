import cv
import pygame
import math
import numpy
import sys
import time
import gzip
import pickle

def post_process(vectors):
	
	size = len(vectors) / 2

	vec = zip(vectors[:size], vectors[size:])

	size_x = Vision.res_work[0]
	size_y = Vision.res_work[1]

	i = size_x * size_y / 2

	x,y = zip(*vec[i:i+size_x])

	return x + y

class Vision:
	# Scale of motion vector array (more means less !)
	scale = 64

	# Size of detection window
	window = 7

	res_input = (640, 480)

	res_work = (res_input[0] / scale, res_input[1] / scale)

	def gen_palette_fire(self):
		gstep, bstep = 75, 150
		cmap = numpy.zeros((256, 3))
		cmap[:,0] = numpy.minimum(numpy.arange(256)*3, 255)
		cmap[gstep:,1] = cmap[:-gstep,0]
		cmap[bstep:,2] = cmap[:-bstep,0]
		return cmap

	def gen_palette_gray(self):
		return [(x, x, x) for x in range(256)]

	def frame2surface(self, frame):
		frame_rgb = cv.CreateMat(frame.height, frame.width, cv.CV_8UC3)
		cv.CvtColor(frame, frame_rgb, cv.CV_BGR2RGB)

		return pygame.image.frombuffer(frame_rgb.tostring(), cv.GetSize(frame_rgb), "RGB")

	def frame2gray(self, frame):
		frame_gray = cv.CreateMat(frame.height, frame.width, cv.CV_8UC1)
		cv.CvtColor(frame, frame_gray, cv.CV_BGR2GRAY)

		return frame_gray

	def drawframe(self, frame, velx, vely):
		srfc = pygame.image.frombuffer(frame.tostring(), cv.GetSize(frame), "P")
		srfc.set_palette(self.palette)
		self.screen.blit(srfc, (0, 0))

		for x in range(self.res_work[0]):
			for y in range(self.res_work[1]):
				valx = (cv.Get2D(self.velx, y, x)[0] * self.scale)
				valy = (cv.Get2D(self.vely, y, x)[0] * self.scale)

				basex = x * self.scale + self.scale / 2
				basey = y * self.scale + self.scale / 2
#			print self.res_work[0], self.res_work[1], valx, x, y

				pygame.draw.line(self.screen, self.red, (basex, basey), (round(basex+valx), round(basey+valy)))

		pygame.display.flip()


	def img2ary(self, img):
		a = numpy.fromstring(img.tostring(), numpy.float32)
		a.shape = cv.GetSize(img)
		return a

	def __init__(self, title = "Vision"):
		self.red = pygame.Color("red")
		self.cap = cv.CaptureFromCAM(-1)

		frame_raw = cv.QueryFrame(self.cap)

		cv.SetCaptureProperty(self.cap, cv.CV_CAP_PROP_FRAME_WIDTH, self.res_input[0]);
		cv.SetCaptureProperty(self.cap, cv.CV_CAP_PROP_FRAME_HEIGHT, self.res_input[1]);

		self.screen = pygame.display.set_mode(self.res_input)
		self.palette = self.gen_palette_gray()

		pygame.display.set_caption(title)

		self.velx = cv.CreateImage(self.res_work, cv.IPL_DEPTH_32F, 1)
		self.vely = cv.CreateImage(self.res_work, cv.IPL_DEPTH_32F, 1)

		self.frame_new = cv.CreateImage(self.res_work, cv.IPL_DEPTH_8U, 1)
		self.frame_old = cv.CreateImage(self.res_work, cv.IPL_DEPTH_8U, 1)

		self._query_frame_new()

	def _query_frame_new(self):
		frame_raw = cv.QueryFrame(self.cap)
		frame_gray = self.frame2gray(frame_raw)
		cv.Resize(frame_gray, self.frame_new);

		return frame_gray

	def frame(self):
		self.frame_old, self.frame_new = self.frame_new, self.frame_old
		frame = self._query_frame_new()

		cv.CalcOpticalFlowLK(self.frame_old, self.frame_new, (self.window, self.window), self.velx, self.vely)

		self.drawframe(frame, self.velx, self.vely)

		velx_np = self.img2ary(self.velx)
		vely_np = self.img2ary(self.vely)

		return list(velx_np.flatten()) + list(vely_np.flatten())
