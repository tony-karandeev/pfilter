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
oneDistanceOnly = False

def Property(func):
	return property(**func())

class Maze:
	SQUARE_SIZE = 50.0
	def __init__(self, fname, beaconCount):
		self.map = []
		lines = open(fname).read().splitlines()
		for l in lines:
			self.map.append([])
			for c in l:
				if c == ' ':
					self.map[-1].append(True)
				else:
					self.map[-1].append(False)
		# initialize random beacons
		self.beacons = []
		for i in range(beaconCount):
			x = random.randint(0, self.totalWidth())
			y = random.randint(0, self.totalHeight())
			self.beacons.append((x, y))

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

	def distFromBeacon(self, p):
		"""
			Gives distance from p to the closest beacon
		"""
		minDist2 = 100500
		for beacon in self.beacons:
			dx = p[0] - beacon[0]
			dy = p[1] - beacon[1]
			dst2 = dx**2 + dy**2
			if dst2 < minDist2:
				minDist2 = dst2
		return np.sqrt(minDist2)
	def distsFromBeacons(self, p):
		return [(p[0]-b[0])**2 + (p[1]-b[1])**2 for b in self.beacons]
	def sumDistFromBeacons(self, p):
		"""
			Gives sum of square distances from each beacon to p
		"""
		return sum(distsFromBeacons)


class Robot(Particle):
	STEP_SIZE = Maze.SQUARE_SIZE / 10.0

	def __init__(self, params, constParams, w=1, noisy=False, noiseFunc=None):
		if noisy and noiseFunc is None:
			raise ValueError('Particle that is noisy requires it''s ''noiseFunc'' parameter not to be None')
		self.params = params if not noisy else noiseFunc(params)
		self.constParams = constParams
		self.w = w
		#robot-specific fields further
		self.lastPointFree = True
		self.distFromBeacon = self.maze.distFromBeacon(self.p)

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
		if oneDistanceOnly:
			self.distFromBeacon = self.maze.distFromBeacon(self.p)
		else:
			self.distsFromBeacons = self.maze.distsFromBeacons(self.p)
		return deltaAngle
				

			


def maze2draw(point):
	#x and y are swapped intentionally
	y = point[0] / Maze.SQUARE_SIZE * SQUARE_SIZE_PX
	x = point[1] / Maze.SQUARE_SIZE * SQUARE_SIZE_PX
	return int(x), int(y)

def draw(img, robot, pp):
	img[:,:] = 0
	maze = robot.maze
	#draw maze
	for x in range(maze.width()):
		for y in range(maze.height()):
			if maze.map[x][y]:
				p1 = (y*SQUARE_SIZE_PX, x*SQUARE_SIZE_PX)
				p2 = ((y+1)*SQUARE_SIZE_PX, (x+1)*SQUARE_SIZE_PX)
				cv2.rectangle(img, p1, p2, (255,255,255), -1)
	#draw beacons
	for b in maze.beacons:
		p = maze2draw(b)
		p = (int(p[0]), int(p[1]))
		cv2.circle(img, p, 3, (179, 30, 171), -1)
	#draw robot
	pnt = maze2draw(robot.p)
	pnt = (int(pnt[0]), int(pnt[1]))
	cv2.circle(img, pnt, 5, (0,0,255), -1)
	#draw particles
	for p in pp:
		mazePoint = (p.params[0], p.params[1])
		pnt = maze2draw(mazePoint)
		cv2.circle(img, pnt, 2, (255,0,0), -1)


def main():
	pcount = 2000
	beaconCnt = 10
	sigma = 500
	mazefile = 'maze.txt'
	
	argcnt = len(sys.argv)
	if argcnt < 2:
		print 'Using particle count: %d' % pcount
	else:
		pcount = int(sys.argv[1])
	if argcnt < 3:
		print 'Using beacon count: %d' % beaconCnt
	else:
		beaconCnt = int(sys.argv[2])
	if argcnt < 4:
		print 'Using sigma: %d' % sigma
	else:
		sigma = float(sys.argv[3])
	if argcnt < 5:
		print 'Using maze from file: %s' % mazefile
	else:
		mazefile = sys.argv[4]


	maze = Maze(mazefile, beaconCnt)

	def rndParams():
		x, y = maze.randomFreePlace()
		angle = uni(0, 2*np.pi)
		return [x, y, angle]
	nlimit = Robot.STEP_SIZE / 10.0
	def noiser(params):
		x = params[0] + uni(-nlimit, nlimit)
		y = params[1] + uni(-nlimit, nlimit)
		angle = params[2] + uni(-np.pi/100, np.pi/100)
		return [x, y, angle]
	def error(p, inputData):
		"""p is a particle, inputData equals to robot's 'lastPointFree' field after acting"""
		robotLastPointFree = inputData[0]
		wallBumpingError = 0 if p.lastPointFree == robotLastPointFree else 1
		if oneDistanceOnly:
			robotDistFromBeacon = inputData[1]
			beaconDistError = (p.distFromBeacon - robotDistFromBeacon)**2
		else:
			robotDistsFromBeacons = inputData[1]
			beaconDistErrors = []
			for i in range(len(robotDistsFromBeacons)):
				diff = abs(robotDistsFromBeacons[i] - p.distsFromBeacons[i])
				beaconDistErrors.append(diff)
			beaconDistError = sum(beaconDistErrors)
		return wallBumpingError * 100500 + beaconDistError
	

	paul = Robot(rndParams(), maze)
	pf = PFilter(pcount, sigma**2, paul.constParams, rndParams, error, noiser, Robot)


	cv2.namedWindow(winname, cv2.CV_WINDOW_AUTOSIZE)
	img = np.zeros((maze.width() * SQUARE_SIZE_PX, maze.height() * SQUARE_SIZE_PX, 3), np.uint8)
	draw(img, paul, pf.particles)
	cv2.imshow(winname, img)
	cv2.waitKey(0)


	i = 1
	while True:
		random.seed(time.time())
		#print 'Paul moves'
		deltaAngle = paul.act()
		beacondist = paul.distFromBeacon if oneDistanceOnly else paul.distsFromBeacons
		res = pf.step(deltaAngle, [paul.lastPointFree, beacondist])
		print 'step %d' % i
		i += 1
		#print 'step done...'


		draw(img, paul, pf.particles)
		cv2.imshow(winname, img)
		#print 'wait...'
		cv2.waitKey(15)
		#print 'continue'

	cv2.waitKey(0)
	return


if __name__ == '__main__':
	main()



