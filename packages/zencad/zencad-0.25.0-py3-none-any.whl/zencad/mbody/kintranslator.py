#!/usr/bin/env

from zencad.libs.screw import screw
import zencad.mbody.kinematic as kinematic


class kintranslator:
	"""Решает задачу построения динамической модели 
	по кинематическому дерева.
	"""

	FREE_SPACE_MODE = 0
	CONSTRAIT_MODE = 1

	def __init__(self, baseunit, mode=FREE_SPACE_MODE):
		self.baseunit = baseunit
		self.mode = mode

	def build(self):
		self.baseunit.update_pose()
		self.kinframes = kinematic.find_all_kinframes(self.baseunit)
		self.collect_all_kinframe_inertia()

		if self.mode == self.FREE_SPACE_MODE:
			pass

		elif self.mode == self.CONSTRAIT_MODE:
			pass

		self.rigids = [ body.kinframe_body(kin) for kin in self.kinframes ]

		return self.rigids, self.constraits

	def collect_all_kinframe_inertia(self):
		for k in self.kinframes:
			k.collect_inertia()

	def make_constraits(self):
		ret = []
		for k in self.kinframes:
			k.init_constrait()
			ret.append(k.constrait)

	def make_bodies(self):
		ret = []
		for k in self.kinframes:
			k.init_body()
			ret.append(k.constrait)

	def produce_bodies_spdacc(self):
		pass

	def reduce_bodies_spdacc(self):
		pass