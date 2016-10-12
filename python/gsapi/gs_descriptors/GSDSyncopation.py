import os
import sys


if __name__=='__main__':
	sys.path.insert(1, os.path.abspath(os.path.join(__file__,
                                                    os.pardir,
                                                    os.pardir,
                                                    os.pardir)))


from gsapi import GSDescriptor
# import math


class GSDSyncopation(GSDescriptor):
	"""
	Computes the syncopation value from a pattern.
	"""
	def __init__(self):
		GSDescriptor.__init__(self)
		self.weights = []
		self.duration  = 16
		self.note_grid = []


	def get_descriptor_for_pattern(self,pattern):

		if(pattern.duration != self.duration):
			print "Syncopation inputing a pattern of duration %f but expected is %f" % (pattern.duration, self.duration)
			pattern = pattern.getPatternForTimeSlice(0,self.duration)
		if not self.weights :
			self.buildSyncopationWeight(pattern.duration)
		syncopation =0

		self.buildBinarizedGrid(pattern)
		for t in range(self.duration):
			nextT = (t+1)%self.duration
			if  self.note_grid[t] and not self.note_grid[nextT] :
				syncopation+=abs(self.weights[nextT] - self.weights[t])

		return syncopation

		

	def buildSyncopationWeight(self,duration):
		depth = 1
		# numSteps = int(math.log(duration)/math.log(2)
		self.weights = [0] * int(duration)
		thresh  =0
		
		stepWidth = int((duration)*1.0/depth)
		while(stepWidth>thresh):
			for s in range(depth):
				self.weights[s*stepWidth]+=1
			depth=depth*2
			stepWidth = int(duration*1.0/depth)

	def buildBinarizedGrid(self,pattern):
		self.note_grid = [0] * self.duration
		for i in range(self.duration):
			self.note_grid[i] = len(pattern.getActiveEventsAtTime(i))



