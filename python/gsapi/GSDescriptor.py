import logging
from gsapi import GSPattern


class GSDescriptor(object):

	def __init__(self):
		pass

	def get_descriptor_for_pattern(self, pattern):
		"""Compute an unique value for a given pattern.
		It can be a sliced part of a bigger one.
		"""
		raise NotImplementedError("Martin should have implemented this ;-)")
