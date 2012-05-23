from exceptions import *
import random as rnd
import bisect
import numpy as np


class WeightedDistribution:
	def __init__(self, items):
		self.items = [item for item in items if item.w > 0];
		total_weight = 0.0
		self.distribution = []
		for item in self.items:
			total_weight += item.w
			self.distribution.append(total_weight)
		self.total_weight = total_weight

	def pick(self):
		try:
			idx = bisect.bisect_left(self.distribution, rnd.uniform(0, self.total_weight))
			return self.items[idx]
		except IndexError:
			# No items in distribution
			return None


class Particle:
	def __init__(self, params, w=1, noisy=False, add_noise=None):
		if noisy and add_noise is None:
			raise ValueError('Particle that is noisy requires it''s ''add_noise'' function not to be none')
		self.params = np.array(params, np.float32)
		if noisy:
			add_noise(self.params)
		self.w = w

		@classmethod
		def create_random(cls, count, random_params):
			res = []
			for i in range(count):
				params = random_params()
				res.append(cls(params, w=1, noisy=False))
			return res

class PFilter:
	def __init__(self, pcount, sigma2, precisions, random_params, error_func):
		self.PCOUNT = pcount
		self.random_params = random_params
		self.error = error_func
		self.particles = Particle.create_random(self.PCOUNT, self.random_params)
		self.sigma2 = sigma2
		self.precisions = precisions

	def gauss(x):
		return np.e ** -(x**2 / (2*self.sigma2))

	def step(self, input_data=None):
		for p in self.particles:
				err = self.error(p, input_data)
				p.w = float(gauss(err))

		total_weight = sum(p.w for p in self.particles)
		if 0 != total_weight:
			for p in self.particles:
				p.w /= total_weight

		wdist = WeightedDistribution(self.particles)
		new_particles = []
		for _ in self.particles:
			p = wdist.pick()
			if p is None:
				new_p = Particle.create_random(1, self.random_params)[0]
			else:
				new_p = Particle(p.params, w=1, noisy=True)
			new_particles.append(new_p)
			
		new_params = np.array([p.params for p in new_particles], np.float32)
		params_dev = np.std(new_params, dtype=np.float64)

		if (False in [abs(diff) < abs(self.precisions) for diff in params_diff]):
			self.particles = new_particles
			return None
		else:
			return np.mean(new_params, axis=0, dtype=np.float64)


		
		
		

		

