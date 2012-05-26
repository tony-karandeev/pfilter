from exceptions import *
import abc
from random import uniform as uni
import bisect
import numpy as np


class WeightedDistribution:
	def __init__(self, items):
		self.items = [item for item in items if item.w > 0]
		totalWeight = 0.0
		self.distribution = []
		for item in self.items:
			totalWeight += item.w
			self.distribution.append(totalWeight)
		self.totalWeight = totalWeight
	def pick(self):
		try:
			idx = bisect.bisect_left(self.distribution, uni(0, self.totalWeight))
			return self.items[idx]
		except IndexError:
			# No items in distribution
			return None

class Particle(object):
	@abc.abstractmethod
	def __init__(self, params, constParams, w=1, noisy=False, noiseFunc=None):
		pass
	
	@classmethod
	def createRandom(cls, count, rndParamsFunc, constParams):
		res = []
		for i in range(count):
			params = rndParamsFunc()
			res.append(cls(params, constParams, w=1, noisy=False))
		return res

	def act(self, actionParams):
		"""
			This method shall be overriden if particle performs some action together with robot or what it is each step. If it doesn't, just leave this method as it is.
		"""
		pass
		

	@abc.abstractproperty
	def params(self):
		"""
			This property must get parameter list from child's attributes and set child's attributes given such a parameter list
		"""
		pass
	
	@abc.abstractproperty
	def constParams():
		"""Like 'params' property, but deals with parameters that shouldn't be optimised by PFilter."""


class PFilter:
	def __init__(self, pcount, sigma2, constParams, rndParamsFunc, errorFunc, noiseFunc, particleClass):
		if not issubclass(particleClass, Particle):
			raise ValueError('"particleClass" parameter must be subclass of Particle')
		self.pcount = pcount
		self.sigma2 = sigma2
		self.particleConstParams = constParams
		self.randomParams = rndParamsFunc
		self.error = errorFunc
		self.addNoise = noiseFunc
		self.particleClass = particleClass
		self.particles = particleClass.createRandom(self.pcount, self.randomParams, self.particleConstParams)


	def gauss(self, x):
		return np.e ** -(x**2 / (2*self.sigma2))
	
	def step(self, actionParams=None, inputData=None):
		for p in self.particles:
			p.act(actionParams)
			err = self.error(p, inputData)
			p.w = self.gauss(err)

		# with our implementation of WeightedDistribution
		# we need not normalize weights
		wdist = WeightedDistribution(self.particles)
		newParticles = []
		for _ in self.particles:
			p = wdist.pick()
			if p is None:
				newP = self.particleClass.createRandom(1, self.randomParams, self.particleConstParams)[0]
			else:
				newP = self.particleClass(p.params, self.particleConstParams, w=1, noisy=True, noiseFunc=self.addNoise)
			newParticles.append(newP)
		self.particles = newParticles
		return


























