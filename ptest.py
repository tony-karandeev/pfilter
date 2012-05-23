from pfilter import *
import cv
import random

square_width = 512
square_height = 512
square_img = cv.CreateMat(square_width, square_height, cv.CV_8UC1)

def error_func(p, input_data=None):
	pp = p.params
	dx = pp.x - square_width // 2
	dy = pp.y - square_height // 2
	return dx**2 + dy**2

def random_place():
	params = []
	params.append(random.uniform(0, square_width))
	params.append(random.uniform(0, square_height))
	return params

pf = PFilter(1500, 1000**2, (1, 1), random_place, error_func)

def iterate():
	sq.draw()
	pp = pf.particles
	for p in pp:
		cv.Circle(square_img, (int(p.x), int(p.y)), 2, cv.ScalarAll(255), -1)
	cv.ShowImage('w', square_img)
	pf.step()


def main():
	cv.NamedWindow('w', cv.CV_WINDOW_AUTOSIZE)
	while True:
		sq.draw()
		pp = pf.particles
		for p in pp:
			x = p.params[0]
			y = p.params[1]
			cv.Circle(square_img, (int(x), int(y)), 2, cv.ScalarAll(255), -1)
		cv.ShowImage('w', square_img)
		pf.step()

		cv.WaitKey(50)


if __name__ == '__main__':
	main()
