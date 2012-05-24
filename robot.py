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
	def total_width(self):
		return self.width() * self.SQUARE_SIZE
	def total_height(self):
		return self.height() * self.SQUARE_SIZE
	def square(self, p):
		x = p[0] // self.SQUARE_SIZE
		y = p[1] // self.SQUARE_SIZE
		return int(x), int(y)

	def random_place(self):
		return uni(0, self.total_width()), uni(0, self.total_height())
	def random_free_place(self):
		while True:
			res = self.random_place()
			if self.is_free(res):
				return res

	def is_free(self, p):
		"""
			Determines whether current point p is empty or does it contain wall.
		"""
		maxx = self.total_width()
		maxy = self.total_height()
		sx, sy = self.square(p)
		print 'sx, sy == ', (sx, sy)
		bounds_check = p[0] >= 0 and p[1] >= 0 and p[0] < maxx and p[1] < maxy
		if not bounds_check:
			return False
		square_check = self.map[sx][sy]
		return square_check

		

class Robot:
	STEP_SIZE = Maze.SQUARE_SIZE / 10.0
	def __init__(self, p, maze):
		self.p = p
		self.maze = maze
	def move(self):
		"""
			Moves robot by STEP_SIZE in random direction.
		"""
		x, y = self.p
		angle = 2 * np.pi * uni(0, 1)
		x += self.STEP_SIZE * np.sin(angle)
		y += self.STEP_SIZE * np.cos(angle)
		dx = dy = 0
		if self.maze.is_free((x, y)):
			dx = x - self.p[0]
			dy = y - self.p[1]
			self.p = x, y
		else:
			pass
		return (x, y), (dx, dy)

def maze2draw(point):
	#x and y are swapped intentionally
	y = point[0] / Maze.SQUARE_SIZE * SQUARE_SIZE_PX
	x = point[1] / Maze.SQUARE_SIZE * SQUARE_SIZE_PX
	return int(x), int(y)

def draw(img, maze, robot, pp):
	img[:,:] = 0
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
		maze_point = (p.params[0], p.params[1])
		pnt = maze2draw(maze_point)
		cv2.circle(img, pnt, 2, (255,0,0), -1)


def main():
	maze = Maze('maze.txt')
	paul = Robot(maze.random_free_place(), maze)

	#particle filter setup
	prec = Robot.STEP_SIZE
	rnd_params = lambda: (uni(0, maze.total_width()), uni(0, maze.total_height()))
	error = lambda p, free: 1.0 if maze.is_free((p.params[0], p.params[1])) == free else 0.0
	nlimit = Robot.STEP_SIZE / 3.0
	noiser = lambda (x, y): (x + uni(-nlimit, nlimit), y + uni(-nlimit, nlimit))
	pf = PFilter(1500, 1000**2, (prec, prec), rnd_params, error, noiser)


	cv2.namedWindow(winname, cv2.CV_WINDOW_AUTOSIZE)
	img = np.zeros((maze.width() * SQUARE_SIZE_PX, maze.height() * SQUARE_SIZE_PX, 3), np.uint8)
	draw(img, maze, paul, pf.particles)
	cv2.imshow(winname, img)
	cv2.waitKey(0)


	while True:
		random.seed(time.time())
		print 'Paul moves'
		target_p, dp = paul.move()
		target_is_free = (0, 0) == dp
		print 'Paul moved by ', dp
		res = pf.step(dp, target_is_free)
		print 'step done...'
		if res is None:
			draw(img, maze, paul, pf.particles)
			cv2.imshow(winname, img)
			print 'wait...'
			cv2.waitKey(500)
			print 'continue'
			continue
		else:
			draw(img, maze, pf.particles)
			cv2.imshow(winname, img)
			print 'res == ', res
			break
	cv2.waitKey(0)
	return


if __name__ == '__main__':
	main()



