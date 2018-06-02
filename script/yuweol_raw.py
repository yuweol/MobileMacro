import sys, numpy

from config import Config
from yuweol_parser import Parser

class RawNode():
	def __init__(self, time, x, y):
		self.time = time
		self.x = int(x, 16)
		self.y = int(y, 16)

	def __str__(self):
		msg = "[" + str(self.time) + "] - (" + self.coord[0] + ", " + self.coord[1] + ")"
		return msg
		
	def coord_normalize(self, coord):
		return self.asc_to_coord(self.coord_to_asc(coord))
		
	def coord_to_asc(self, coord):
		min = int(config.min_asc, 16)
		max = int(config.max_asc, 16)
		max_coord = int(config.max_coord, 16)
		size = max - min + 1
		unit = float(max_coord / size)
		
		coord_int = int(coord, 16)
		index = int(float(coord_int) / unit) + min
		if (index > max) or (index < min):
			raise RuntimeError("index is overflowed (index : " + str(index) + ", coord : " + coord + ")")

		return chr(index)
		
	def asc_to_coord(self, asc):
		min = int(config.min_asc, 16)
		max = int(config.max_asc, 16)
		max_coord = int(config.max_coord, 16)
		size = max - min + 1
		unit = float(max_coord / size)
		
		return hex(int((ord(asc) - min) * unit))
		
	def format_asc(self):
		return self.coord_to_asc(self.coord[0]) + self.coord_to_asc(self.coord[1])
		
	def getTime(self):
		return self.time
		
	def getCoord(self):
		return self.coord
		
	#This method is for generating vector based on direction
	#For calculating direction, previous coordination is required
	#Expression : (LeftTop, Top, RightTop, Left, Center, Right, LeftBottom, Bottom, RightBottom)
	def vectorize_direction(self, prevCoord):
		#Variable delarations
		prevX, prevY = prevCoord
		curX, curY = self.coord
		leftFlag = False
		rightFlag = False
		topFlag = False
		bottomFlag = False
		centerXFlag = False
		centerYFlag = False		

		#Change them from hex string to integer
		prevX = int(prevX, 16)
		prevY = int(prevY, 16)
		curX = int(curX, 16)
		curY = int(curY, 16)

		#Gather information about derection for generating vector
		#Consider bellow base knowledge
		#Left : 0, Right : 0x8000, Top : 0, Bottom : 0x8000
		if prevX > curX:
			leftFlag = True
		elif prevX < curX:
			rightFlag = True
		else:
			centerXFlag = True

		if prevY > curY:
			topFlag = True
		elif prevY < curY:
			bottomFlag = True
		else:
			centerYFlag = True

		ret = None
		if leftFlag == True:
			if rightFlag == True or centerXFlag == True:
				raise RuntimeError("unexpected direction")
			if topFlag == True:
				ret = [ 1, 0, 0, 0, 0, 0, 0, 0, 0 ]
			if bottomFlag == True:
				if ret != None:
					raise RuntimeError("unexpected direction")
				else:
					ret = [ 0, 0, 0, 0, 0, 0, 1, 0, 0 ]
			if centerYFlag == True:
				if ret != None:
					raise RuntimeError("unexpected direction")
				else:
					ret = [ 0, 0, 0, 1, 0, 0, 0, 0, 0 ]
		if rightFlag == True:
			if leftFlag == True or centerXFlag == True:
				raise RuntimeError("unexpected direction")
			if topFlag == True:
				if ret != None:
					raise RuntimeError("unexpected direction")
				else:
					ret = [ 0, 0, 1, 0, 0, 0, 0, 0, 0 ]
			if bottomFlag == True:
				if ret != None:
					raise RuntimeError("unexpected direction")
				else:
					ret = [ 0, 0, 0, 0, 0, 0, 0, 0, 1 ]
			if centerYFlag == True:
				if ret != None:
					raise RuntimeError("unexpected direction")
				else:
					return [ 0, 0, 0, 0, 0, 1, 0, 0, 0 ]
		if centerXFlag == True:
			if leftFlag == True or rightFlag == True:
				raise RuntimeError("unexpected direction")
			if topFlag == True:
				if ret != None:
					raise RuntimeError("unexpected direction")
				else:
					ret = [ 0, 1, 0, 0, 0, 0, 0, 0, 0 ]
			if bottomFlag == True:
				if ret != None:
					raise RuntimeError("unexpected direction")
				else:
					ret = [ 0, 0, 0, 0, 0, 0, 0, 1, 0]
			if centerYFlag == True:
				if ret != None:
					raise RuntimeError("unexpected direction")
				else:
					ret = [ 0, 0, 0, 0, 1, 0, 0, 0, 0 ]
		
		#I think, I don't need to make them numpy list here.
		#Because, this class doens't do any operation related to numpy.
		#I want to make this program loosely coupled to external librarires.
		return ret
	
	@staticmethod
	def vectorize_direction_zero():
		return [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
		
	@staticmethod
	def vectorize_direction_one():
		return [ 1, 1, 1, 1, 1, 1, 1, 1, 1 ]
		
	@staticmethod
	def is_zero_vector(vector):
		sum = 0
		for e in vector:
			sum += e
		if sum == 0:
			return True
		else:
			return False
		
	@staticmethod
	def vector_add(src, dst):
		if len(src) != len(dst):
			raise RuntimeError("unexpected vector length")
		else:
			sum = src
			for i in range(0, len(dst)):
				sum[i] = sum[i] + dst[i]
			return sum
		
class PointVector():
	def __init__(self, data, size):
		maxsize = int(int(Config.max_coord, 16) / size)
		self.point = numpy.zeros(maxsize * maxsize)
		for element in data:
			x, y = element.getCoord()
			x = int(int(x, 16) / size)
			y = int(int(y, 16) / size)
			self.point[x*maxsize + y] += 1
	
	@staticmethod
	def get_zero(size):
		maxsize = int(int(Config.max_coord, 16) / size)
		return numpy.zeros(maxsize*maxsize)
			
	@staticmethod
	def get_base(size):
		maxsize = int(int(Config.max_coord, 16) / size)
		return numpy.ones(maxsize*maxsize)

class Raw():
	def __init__(self, path):
		self.nodes = []
		p = Parser(path)
		i = 0
		x_coord = None
		x_time = None
		init_time = p.nodes[0].time
		token_size = len(p.nodes)

		while i < token_size:
			token = p.nodes[i]
			action = token.action
			
			if (x_coord == None) and (action == "ABS_MT_POSITION_X"):
				x_coord = token.value
				x_time = token.time - init_time
			elif (x_coord == None) and (action == "ABS_MT_POSITION_Y"):
				raise RuntimeError("No X coord before Y coord (token index : " + str(i) + ")")
			elif (x_coord != None) and (action == "ABS_MT_POSITION_X"):
				raise RuntimeError("No Y coord (token index : " + str(i) + ")")
			elif (x_coord != None) and (action == "ABS_MT_POSITION_Y"):
				y_time = token.time - init_time
				if x_time != y_time:
					raise RuntimeError("X and Y coord has different time")
				self.nodes.append(\
					RawNode(x_time, x_coord, token.value))
				x_coord = None
			i += 1
			
	def size(self):
		return len(self.vectors)
		
	def get(self, index):
		return self.vectors[index]
		
	def format_asc(self, start, end):
		msg = ""
		for i in range(start, end):
			msg += self.vectors[i].format_asc()
		return msg
		
	def append(self, vector):
		self.vectors.append(vector)
		
	def shrink(self, idx):
		self.vectors = self.vectors[:idx]