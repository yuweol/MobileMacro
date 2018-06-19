#!/usr/bin/env python
class TimeClusterNode():
	def __init__(self, startTime, endTime):
		self.startTime = startTime
		self.endTime = endTime
		self.nodes = []
	
	def vector(self, size_x, size_y):
		ret = [0,] * (size_x * size_y)
		for i in range(0, len(self.nodes)):
			ret[self.nodes[i].region] += 1
		return ret

def alloc_clusters(time_slot, start_time, end_time):
	total_time = int(end_time - start_time)
	slot_number = int(total_time / time_slot)

	clusters = []
	for i in range(0, slot_number):
		node = TimeClusterNode(i * time_slot, (i+1) * time_slot)
		clusters.append(node)

	return clusters

class TimeCluster():
	def __init__(self, raw, time_slot):
		self.time_slot = time_slot
		self.nodes = alloc_clusters(time_slot, raw.nodes[0].time, raw.nodes[-1].time)
		for i in range(0, len(raw.nodes)):
			self.assign(raw.nodes[i])

	def assign(self, rawNode):
		idx = int(rawNode.time / self.time_slot)
		if idx < len(self.nodes):
			self.nodes[idx].nodes.append(rawNode)

	def density(self):
		times = []
		densities = []
		for i in range(0, len(self.nodes)):
			density = float("{0:.2f}".format(float(
				len(self.nodes[i].nodes)) / float(self.time_slot)))
			times.append(i * self.time_slot)
			densities.append(density)
		return times, densities

	def getTouches(self, sTime, eTime):
		sIdx = sTime / self.time_slot
		eIdx = eTime / self.time_slot
		if eIdx > self.nodes[-1].endTime:
			eIdx = self.nodes[-1].endTime

		touches = []
		for i in range(sIdx, eIdx):
			touches.append(self.nodes[i].nodes)

		return touches

	def __str__(self):
		ret = ""
		for i in range(0, len(self.nodes)):
			ret += "[" + str(self.nodes[i].startTime) + " ~ " + \
				str(self.nodes[i].endTime) + "] " + \
				str(len(self.nodes[i].nodes)) + "(" + \
				"{0:.2f}".format(float(len(self.nodes[i].nodes)) / \
					float(self.time_slot)) + ")\n"
		return ret
