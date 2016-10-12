from GSPattern import GSPattern


class GSPatternTransformer(object):
	""" Base class for defining a transform algorithm.

	Such class needs to provide the following functions:
		- configure(self, dict): configure the current transformer based on
		  implementation specific parameters passed in dictionary argument.
		- transform_pattern(self, GSPattern): return a transformed version
		  of GSPattern
	"""


	def __init__(self):
		self.type = "None"

	def configure(self, param_dict):
		"""Configure the current transformer based on implenmentation specific
		parameters passed in dictionary argument.

		Args:
			param_dict: a dictionnary filed with configuration values.
		"""
		raise NotImplementedError("Martin should have implemented this ;-)")


	def transform_pattern(self, pattern):
		"""Returns a transformed version of GSPattern.

		Args:
			pattern: the pattern to be transformed
		"""
		raise NotImplementedError("Martin should have implemented this ;-)")
