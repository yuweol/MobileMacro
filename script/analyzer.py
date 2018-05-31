from yuweol_raw import Raw
from scipy import spatial
import numpy, math

from config import Config

class AnalyzerNode():
	def __init__(self):
		self.region = -1
		self.region_distance = -1
		self.region_direction = -1
		
class BurstNode:
	def __init__(self):
		self.starttime = -1.0
		self.finishtime = -1.0
		self.cnt = 0
			
class Analyzer():
	def __init__(self, raw):
		self.raw = raw
		self.nodes = []
		self.bursts = []
		for i in range(0, len(raw.nodes)):
			self.nodes.append(AnalyzerNode())
			
	#Only burst touches will be remained
	def normalize_burst_touch(self, max):
		for i in reversed(range(1, len(self.raw.nodes))):
			if self.raw.nodes[i].time - self.raw.nodes[i-1].time >= max:
				self.raw.nodes.pop(i)

	#Devide screen into X regions, and allocate a region to each touch
	#based on their touch coordinates. And then calcaultes the distance
	#between each touch regions based on Manhatten distance
	def set_region_label(self, size_x, size_y):
		max_x = int(Config.max_coord, 16)
		max_y = int(Config.max_coord, 16)
		unit_x = math.ceil(float(max_x / size_x))
		unit_y = math.ceil(float(max_y / size_y))
		
		for i in range(0, len(self.raw.nodes)):
			#Set region
			region_x = int(self.raw.nodes[i].x / unit_x)
			if region_x == unit_x:
				region_x -= 1
			region_y = int(self.raw.nodes[i].y / unit_y)
			if region_y == unit_y:
				region_y -= 1
			
			if (region_x >= size_x) or (region_y >= size_y):
				raise RuntimeError("unexpected")

			region = (region_y * size_x) + region_x
			self.nodes[i].region = region
			if i > 0:
				#Set region distance
				if self.nodes[i-1].region >= self.nodes[i].region:
					big = self.nodes[i-1].region
					small = self.nodes[i].region
				else:
					big = self.nodes[i].region
					small = self.nodes[i-1].region
				distance = int((big - small) / size_x)
				small += (distance * size_x)
				self.nodes[i].region_distance = distance + big - small
				
				#Set region direction
				lFlag = False
				rFlag = False
				xFlag = False
				tFlag = False
				bFlag = False
				yFlag = False
				
				prevYIdx = int(self.nodes[i-1].region / size_x)
				curYIdx = int(self.nodes[i].region / size_x)
				if curYIdx > prevYIdx:
					bFlag = True
				elif curYIdx == prevYIdx:
					yFlag = True
				else:
					tFlag = True
				
				prevXIdx = self.nodes[i-1].region % size_x
				curXIdx = self.nodes[i].region % size_x
				if curXIdx > prevXIdx:
					rFlag = True
				elif curXIdx == prevXIdx:
					xFlag = True
				else:
					lFlag = True
					
				if lFlag and tFlag:
					self.nodes[i].region_direction = 0
				elif xFlag and tFlag:
					self.nodes[i].region_direction = 1
				elif rFlag and tFlag:
					self.nodes[i].region_direction = 2
				elif lFlag and yFlag:
					self.nodes[i].region_direction = 3
				elif xFlag and yFlag:
					self.nodes[i].region_direction = 4
				elif rFlag and yFlag:
					self.nodes[i].region_direction = 5
				elif lFlag and bFlag:
					self.nodes[i].region_direction = 6
				elif xFlag and bFlag:
					self.nodes[i].region_direction = 7
				elif rFlag and bFlag:
					self.nodes[i].region_direction = 8
				else:
					raise RuntimeError("unexpected")
			else:
				#Set region 
				self.nodes[i].region_distance = 0
				
				#Set region direcition
				self.nodes[i].region_direction = 0
				
	#Analzye touch intervals between most clicked coordinates
	def analyze_interval_most_clicked_coord(self):
		maxcoords = self.analyze_coord_most_clicked()
		
		maxinterval = 0
		maxcoord = None
		for maxcoord in maxcoords:
			intervals = analyze_interval_coord(maxcoord)
			values = list(intervals.values())
			values.sort()
			localmaxinterval = values[0]
			localmaxcoord = None
			for key in intervals.keys():
				if interval[key] == maxinterval:
					localmaxcoord = key
					break
			if localmaxinterval > maxinterval:
				maxcoord = localmaxcoord
			
		return maxcoord, maxinterval
		
	#Analyze touch coordinates of most clickced coordinates
	def analyze_coord_most_clicked(self):
		temp = {}
		for i in range(0, len(self.vectors.vectors)):
			key = self.vectors.vectors[i].coord
			try:
				temp[key] += 1
			except KeyError:
				temp[key] = 1
				
		values = list(temp.values())
		maxval = values[0]
		
		maxcoords = []
		for key in temp.keys():
			if temp[key] == maxval:
				maxcoords.append(key)
				
		return maxcoords
	
	#Analyze interval between a specific touches
	def analyze_interval_coord(self, coord):
		result = {}
		prevTime = 0
		for i in range(0, len(self.vectors.vectors)):
			if coord == self.vectors.vectors[i].coord:
				if prevTime == 0:
					interval = 0
				else:
					interval = float("{0:.2f}".format(self.vectors.vectors[i].time)) - prevTime
				try:
					result[interval] += 1
				except KeyError:
					result[interval] = 1
		return result
			
	#Get interval distribution between every touches
	def get_interval_distribution(self):
		nodes = self.vectors.vectors
		result = {}
		result[0] = 1
		
		for i in range(1, len(nodes)):
			interval = float("{0:.2f}".format(nodes[i].time - nodes[i-1].time))
			try:
				result[interval] += 1
			except KeyError:
				result[interval] = 1
		return result
		
	#Get touch distribution only if the same coordinates
	def get_interval_distribution_with_same_coord(self):
		nodes = self.vectors.vectors
		temp = {}
		
		for i in range(0, len(nodes)):
			x = int(nodes[i].coord[0], 16)
			y = int(nodes[i].coord[1], 16)
			key = (x, y)
			try:
				prevTime = temp[key][0]
			except KeyError:
				prevTime = 0
			
			try:
				internalM = temp[key][1]
			except KeyError:
				internalM = {}
				
			if prevTime == 0:
				interval = 0
			else:
				interval = nodes[i].time - prevTime
			
			try:
				internalM[interval] += 1
			except KeyError:
				internalM[interval] = 1
			
			temp[key] = (prevTime, internalM)
		
		result = {}
		for x,y in list(temp.keys()):
			for interval in list(temp[(x,y)][1].keys()):
				key = (x, y, interval)
				try:
					result[key] += 1
				except KeyError:
					result[key] = 1

		return result
