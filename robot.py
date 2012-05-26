import os
import sys
import time
import random
from random import uniform as uni
import numpy as np
import cv2
from pfilter import *

SQUARE_SIZE_PX = 100

winname = 'Maze'
maze = None

def Property(func):
	return property(**func())

class Maze:
	SQUARE_SIZE = 50.0
	def __init__(self, fname):
		self.map = []
		lines = open(fname).read().splitlines()
		for l in lines:
			self.map.append([])
			for c in l:
				if c == ' ':
					self.map[-1].append(True)
				else:
					self.map[-1].append(False)
	def width(self):
		return len(self.map)
	def height(self):
		return max([len(row) for row in self.map])
	def totalWidth(self):
		return self.width() * self.SQUARE_SIZE
	def totalHeight(self):
		return self.height() * self.SQUARE_SIZE
	def square(self, p):
		x = p[0] // self.SQUARE_SIZE
		y = p[1] // self.SQUARE_SIZE
		return int(x), int(y)

	def randomPlace(self):
		return uni(0, self.totalWidth()), uni(0, self.totalHeight())
	def randomFreePlace(self):
		while True:
			res = self.randomPlace()
			if self.isFree(res):
				return res

	def isFree(self, p):
		"""
			Determines whether current point p is empty or does it contain wall.
		"""
		maxx = self.totalWidth()
		maxy = self.totalHeight()
		sx, sy = self.square(p)
		boundsCheck = p[0] >= 0 and p[1] >= 0 and p[0] < maxx and p[1] < maxy
		if not boundsCheck:
			return False
		squareCheck = self.map[sx][sy]
		return squareCheck


class Robot(Particle):
	STEP_SIZE = Maze.SQUARE_SIZE / 25.0

	def __init__(self, params, constParams, w=1, noisy=False, noiseFunc=None):
		if noisy and noiseFunc is None:
			raise ValueError('Particle that is noisy requires it''s ''noiseFunc'' parameter not to be None')
		self.params = params if not noisy else noiseFunc(params)
		self.constParams = constParams
		self.w = w
		#robot-specific fields further
		self.lastPointFree = True

	@Property
	def params():
		doc = 'Constructs parameter list from attributes and update attributes given the parameter list'
		def fget(self):
			return [self.p[0], self.p[1], self.angle]
		def fset(self, value):
			if len(value) != 3:
				raise ValueError('Setter of "params" property expects length of the list to be exactly 3')
			self.p = (value[0], value[1])
			self.angle = value[2]
		fdel = None
		return locals()
	@Property
	def constParams():
		doc = 'Like "params" property, but deals with parameters that shouldn''t be optimized by PFilter.'
		def fget(self):
			return self.maze
		def fset(self, val):
			self.maze = val
		fdel = None
		return locals()

	def act(self, actionParams=None):
		"""
		Moves robot/particle in direction denoted by self.angle by STEP_SIZE.
		If there is a wall on the way, robot stays where he is and sets
		self.lastPointFree to False, otherwise sets it to True.
		It returns (dx, dy) where he wanted to move,
		no matter did he actually go there or not.
		actionParams parameter is not currently used.
		"""
		dx = self.STEP_SIZE * np.sin(self.angle)
		dy = self.STEP_SIZE * np.cos(self.angle)
		x, y = (self.p[0] + dx, self.p[1] + dy)
		deltaAngle = 0
		if self.maze.isFree((x, y)):
			self.p = x, y
			self.lastPointFree = True
		else:
			# change direction so that robot don't stick in the wall
			if not actionParams is None:
				deltaAngle = actionParams
				self.angle += deltaAngle
			else:
				newAngle = uni(0, 2*np.pi)
				deltaAngle = newAngle - self.angle
				self.angle += deltaAngle
			self.lastPointFree = False
		return deltaAngle
				

			


def maze2draw(point):
	#x and y are swapped intentionally
	y = point[0] / Maze.SQUARE_SIZE * SQUARE_SIZE_PX
	x = point[1] / Maze.SQUARE_SIZE * SQUARE_SIZE_PX
	return int(x), int(y)

def draw(img, robot, pp):
	img[:,:] = 0
	maze = robot.maze
	for x in range(maze.width()):
		for y in range(maze.height()):
			if maze.map[x][y]:
				p1 = (y*SQUARE_SIZE_PX, x*SQUARE_SIZE_PX)
				p2 = ((y+1)*SQUARE_SIZE_PX, (x+1)*SQUARE_SIZE_PX)
				cv2.rectangle(img, p1, p2, (255,255,255), -1)
	pnt = maze2draw(robot.p)
	pnt = (int(pnt[0]), int(pnt[1]))
	cv2.circle(img, pnt, 5, (0,0,255), -1)
	for p in pp:
		mazePoint = (p.params[0], p.params[1])
		pnt = maze2draw(mazePoint)
		cv2.circle(img, pnt, 2, (255,0,0), -1)


def main():
	maze = Maze('maze.txt')

	def rndParams():
		x, y = maze.randomFreePlace()
		angle = uni(0, 2*np.pi)
		return [x, y, angle]
	nlimit = Robot.STEP_SIZE / 3.0
	def noiser(params):
		x = params[0] + uni(-nlimit, nlimit)
		y = params[1] + uni(-nlimit, nlimit)
		angle = params[2] + uni(-np.pi/20, np.pi/20)
		return [x, y, angle]
	def error(p, inputData):
		"""p is a particle, inputData equals to robot's 'lastPointFree' field after acting"""
		coeff = 0 if p.lastPointFree == inputData else 1
		return coeff * 100500
	

	
	paul = Robot(rndParams(), maze)
	pf = PFilter(2000, 1000**2, paul.constParams, rndParams, error, noiser, Robot)


	cv2.namedWindow(winname, cv2.CV_WINDOW_AUTOSIZE)
	img = np.zeros((maze.width() * SQUARE_SIZE_PX, maze.height() * SQUARE_SIZE_PX, 3), np.uint8)
	draw(img, paul, pf.particles)
	cv2.imshow(winname, img)
	cv2.waitKey(0)


	while True:
		random.seed(time.time())
		print 'Paul moves'
		deltaAngle = paul.act()
		res = pf.step(deltaAngle, paul.lastPointFree)
		print 'step done...'


		draw(img, paul, pf.particles)
		cv2.imshow(winname, img)
		print 'wait...'
		cv2.waitKey(15)
		print 'continue'

	cv2.waitKey(0)
	return


if __name__ == '__main__':
	main()



