from random import uniform as uni
import cv2
import numpy as np
from pfilter import *

#helper function
def Property(func):
	return property(**func())

sqwid = 512.0
sqhei = 512.0
winname = 'Square test'
img = np.zeros((int(sqhei), int(sqwid)), dtype=np.float32)

class ParticleChild(Particle):
	def __init__(self, params, constParams, w=1, noisy=False, noiseFunc=None):
		if noisy and noiseFunc is None:
			raise ValueError('Particle that is noisy requires it''s ''noiseFunc'' parameter not to be None')
		self.params = params if not noisy else noiseFunc(params)
		self.constParams = constParams
		self.w = w

	@Property
	def params():
		doc = 'Params of particle. X and Y.'
		def fget(self):
			return [self.x, self.y]
		def fset(self, vals):
			if len(vals) != 2:
				raise ValueError('"vals" parameter must contain exactly 2 values')
			self.x = vals[0]
			self.y = vals[1]
		fdel = None
		return locals()
	@Property
	def constParams():
		doc = 'Nothing need to be stored here.'
		def fget(self):
			return []
		def fset(self, vals):
			pass
		fdel = None
		return locals()
	def act(self, actionData):
		# nothing to do here
		pass

def draw(img, particles):
	img[...] = 0
	for p in particles:
		cv2.circle(img, (int(p.x), int(p.y)), 2, 255, -1)

def main():
	noiseLevel = 0.25
	def noiser(params):
		return [x + uni(-noiseLevel, noiseLevel) for x in params]
	def error(p, inputData):
		return np.sqrt((p.x - sqwid/2)**2 + (p.y - sqhei/2)**2)
	def randomParams():
		return [uni(0, sqwid), uni(0,sqhei)]
	pf = PFilter(500, 100**2, [], randomParams, error, noiser, ParticleChild)

	cv2.namedWindow(winname, cv2.CV_WINDOW_AUTOSIZE)
	draw(img, pf.particles)
	cv2.imshow(winname, img)
	cv2.waitKey(0)
	while True:
		pf.step([], [])
		draw(img, pf.particles)
		cv2.imshow(winname, img)
		cv2.waitKey(30)


if __name__ == '__main__':
	main()


