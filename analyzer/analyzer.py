from yuweol_raw import Raw
from scipy import spatial
import numpy, math

from config import Config

#function for simlify logics in Analyzer
def getDirectionChunk(vectors, startIdx, endIdx):
	chunk = vector.vectorize_direction_zero()
	for j in range(startIdx + 1, endIdx):
		chunk = vector.vector_add( chunk, \
			vectors.get(j).vectorize_direction(vectors.get(j-1).getCoord()))
	return chunk

def getChunks(vectors, slot, slot_type):
	#local variables
	chunks = []
	baseIdx = 0
	
	for i in range(0, vectors.size()):
		#Generating vector only after slot is overflowed
		if (slot_type == "time") and \
			(slot < (vectors.get(i).getTime() - vectors.get(baseIdx).getTime())):
				chunks.append(getDirectionChunk(vectors, baseIdx, i - 1))
				baseIdx = i
		elif (slot_type == "click") and \
			(slot < (i - baseIdx)):
				chunks.append(getDirectionChunk(vectors, baseIdx, i - 1))
				baseIdx = i
	return chunks
	
def xysum(x, y, max):
	return (float(x / max) + (10.0 * float(y / max)))
	
def getSimilarities(vectors, slot, slot_type):
	#local variables
	baseIdx = 0
	chunks = []
	similarities = []
		
	#get chunks
	chunks = getChunks(vectors, slot, slot_type)
				
	#calculate cosine similarity between each chunk and 0 vector
	for i in range(0, len(chunks)):
		#we will not calculate similarity if chunk has no information of direciton
		if vector.is_zero_vector(chunks[i]):
			continue
		else:
			similarity = 1 - spatial.distance.cosine(\
				vector.vectorize_direction_one(), chunks[i])
			similarities.append(similarity)
	return similarities
	
def padStringNumber(number, padsize):
	size = padsize - len(number)
	for i in range(0, size):
		number = "0" + number
	return number

class SelfSimilarityAnalyzer():
	def __init__(self, vectors, slot):
		self.vectors = vectors
		self.slot = slot
		self.similarities = []
		
	def analyze_by_time(self):
		self.similarities = getSimilarities(self.vectors, self.slot, "time")
				
	def analyze_by_click(self):
		self.similarities = getSimilarities(self.vectors, self.slot, "click")
		
	def get_similarities(self):
		return self.similarities
		
	def get_std(self):
		return numpy.std(self.similarities)
		
	def get_average(self):
		return numpy.average(self.similarities)

class PointSimilarityAnalyzer():
	def __init__(self, rawdata, area, slot):
		self.rawdata = rawdata
		self.area = area
		self.slot = slot
		self.similarities = []
		
	def analyze(self):
		#Initialize
		baseIdx = 0
		vectors = []
		
		for i in range(0, self.rawdata.size()):
			#Generate vector only after slot is overflowed
			if self.slot < (i - baseIdx):
				vector = PointVector(self.rawdata.vectors[baseIdx:i], self.area)
				vectors.append(vector)
				baseIdx = i
				
		#Calculate cosine similarities between each vector and a vector whose element is all 1
		for i in range(0, len(vectors)):
			self.similarities.append(1 - spatial.distance.cosine( \
				PointVector.get_base(self.area), vectors[i].point))
				
	def get_std(self):
		return numpy.std(self.similarities)		

class FrequencyAnalyzer():
	def __init__(self, vectors, area):
		self.vectors = vectors
		self.frequencies = []
		self.area = area
		
	def analyze(self):
		#local variables & initialization
		checker = {}
		max = 1
		self.frequencies = []
		
		for i in range(1, self.vectors.size()):
			x, y = self.vectors.get(i).getCoord()
			x = padStringNumber(str(int(int(x, 16) / self.area)), 8)
			y = padStringNumber(str(int(int(y, 16) / self.area)), 8)
			
			try:
				checker[x+y] += 1
				if max < checker[x+y]:
					max = checker[x+y]
			except KeyError:
				checker[x+y] = 1
			aver = float(sum(checker.values())) / len(checker.keys())
			self.frequencies.append((max, aver))			

class CoordAnalyzer():
	def __init__(self, vectors):
		self.vectors = vectors
		self.coords = []
	
	def analyze_by_area(self, area):
		#local variables
		self.frequencies = []
		checker = []
		max = int(Config.max_coord, 16)
		
		for i in range(0, self.vectors.size()):
			x, y = self.vectors.get(i).getCoord()
			x = int(x, 16)
			y = int(y, 16)
			coord = xysum(x, y, max)
			self.coords.append((self.vectors.get(i).getTime(), coord))
			
	def get_coords(self):
		return self.coords
		
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
			
	#burst click에 한하여만 조사한다. (이전터치와 간격이 1초 미만으로 차이날 것)
	def normalize_burst_touch(self, max):
		for i in reversed(range(1, len(self.raw.nodes))):
			if self.raw.nodes[i].time - self.raw.nodes[i-1].time >= max:
				self.raw.nodes.pop(i)

	#x개의 영역으로 나누고 node에 해당 영역의 label을 제공 및 distance계산
	def set_region_label(self, size_x, size_y, burst_base):
		max_x = int(Config.max_coord, 16)
		max_y = int(Config.max_coord, 16)
		unit_x = math.ceil(float(max_x / size_x))
		unit_y = math.ceil(float(max_y / size_y))
		
		for i in range(0, len(self.raw.nodes)):
			#region 설정
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
				#region 거리설정
				if self.nodes[i-1].region >= self.nodes[i].region:
					big = self.nodes[i-1].region
					small = self.nodes[i].region
				else:
					big = self.nodes[i].region
					small = self.nodes[i-1].region
				distance = int((big - small) / size_x)
				small += (distance * size_x)
				self.nodes[i].region_distance = distance + big - small
				
				#region 방향설정
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
				#region 거리설정
				self.nodes[i].region_distance = 0
				
				#region 방향설정
				self.nodes[i].region_direction = 0
				
		burst_cnt = 0
		for i in range(0, len(self.nodes) - 1):
			if self.nodes[i+1].time - self.nodes[i].time > burst_base:
				if burst_cnt != 0:
					self.bursts.append(BurstNode(self.nodes[i-burst_cnt].time,\
						self.nodes[i-1].time, burst_cnt))
					burst_cnt = 0
			else:
				burst_cnt += 1
					
				

	#가장 많이 눌린 좌표의 터치 interval 분석
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
		
	#가장 많이 눌린 좌표의 터치 좌표 분석
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
	
	#특정 좌표의 터치 인터벌 분석
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
			
	#터치마다의 간격의 분포 획득(기본적으로 소수2번째 자리는 버리자)
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
		
	#같은 좌표에 한하여 터치 간격 분포 획득
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