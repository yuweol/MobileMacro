import csv, os

from yuweol_raw import Raw

def prepare_output(path, name):
	return open(path + os.sep + name + ".csv", "w")
	
def write_csv(output, title, data):
	writer = csv.writer(output)
	writer.writerow(title)
	for e in data:
		writer.writerow(e)
		
def xysum(x, y, max):
	return (float(x / max) + (10.0 * float(y / max)))

class dumper():
	def __init__(self, path):
		self.path = path
		self.title = []
		self.data = []
		
	def dump_coord(self, a1, a2):
		#local variables & initialization
		a1_data = a1.get_coords()
		a2_data = a2.get_coords()
		a1_size = len(a1_data)
		a2_size = len(a2_data)
		
		#make output file
		output = prepare_output(self.path, "coord")
		
		#make title
		title = [ "time_1", "xysum_1", "time_2", "xysum_2" ]
		
		#make data
		data = []
		maxlen = a1_size
		if maxlen < a2_size:
			maxlen = a2_size
		for i in range(0, maxlen):
			if i >= a1_size:
				element = [ None, None, a2_data[i][0], a2_data[i][1] ]
			elif i >= a2_size:
				element = [ a1_data[i][0], a1_data[i][1], None, None ]
			else:
				element = [ a1_data[i][0], a1_data[i][1], a2_data[i][0], a2_data[i][1] ]
			data.append(element)
		
		#make csv
		write_csv(output, title, data)

	def dump_frequency(self, a1, a2):
		#local variables & initialization
		a1_data = a1.get_frequencies()
		a2_data = a2.get_frequencies()
		a1_size = len(a1_data)
		a2_size = len(a2_data)
		
		#fit size to minimum length
		if a1_size < a2_size:
			a2_data[:a1_size]
		elif a1_size > a2_size:
			a1_data[:a2_size]
			
		#make output file
		output = prepare_output(self.path, "frequency")
		
		#make title
		title = [ "max_1", "max_2", "average_1", "average_2" ]
		
		#make data
		data = []
		for i in range(0, a1_size):
			data.append([a1_data[0], a2_data[0], a1_data[1], a2_data[1]])
			
		#make csv
		write_csv(output, title, data)
		
	def dump_frequency_area(self, a1, a2):
		#validation
		if len(a1) != len(a2):
			raise RuntimeError("unexpected")
		for i in range(0, len(a1)):
			if a1[i].area != a2[i].area:
				raise RuntimeError("unexpected")

		#make output file
		output = prepare_output(self.path, "frequency_unit")
		
		#make title
		title = []
		for i in range(0, len(a1)):
			title.append("max(" + str(a1[i].area) + ")")
			title.append("average(" + str(a1[i].area) + ")")
			
		#make data
		data = []
		maxlen = 0
		for i in range(0, len(a1)):
			if maxlen < len(a1[i].frequencies):
				maxlen = len(a1[i].frequencies)
		for j in range(0, len(a2)):
			if maxlen < len(a2[i].frequencies):
				maxlen = len(a2[i].frequencies)
		
		for i in range(0, maxlen):
			element = []
			for j in range(0, len(a1)):
				if i >= len(a1[j].frequencies) or i >= len(a2[j].frequencies):
					element.append(None)
					element.append(None)
					element.append(None)
					element.append(None)
				else:
					element.append(a1[j].frequencies[i][0] - a2[j].frequencies[i][0])
					element.append(a1[j].frequencies[i][1] - a2[j].frequencies[i][1])
			data.append(element)
			
		#write csv
		write_csv(output, title, data)

	def dump_cosine_similarity(self, a1, a2):
		#local variables & initialization
		a1_data = a1.get_similarities()
		a2_data = a2.get_similarities()
		a1_size = len(a1_data)
		a2_size = len(a2_data)
		
		#make output file
		output = prepare_output(self.path, "similarity")
		
		#make title
		title = [ "similarity_1", "similarity_2" ]
		
		#make data
		data = []		
		maxlen = a1_size
		if maxlen < a2_size:
			maxlen = a2_size
		for i in range(0, maxlen):
			if i >= a1_size:
				element = [ None, a2_data[i] ]
			elif i >= a2_size:
				element = [ a1_data[i], None ]
			else:
				element = [ a1_data[i], a2_data[i] ]
			data.append(element)
		
		#make csv
		write_csv(output, title, data)
		
	def dump_cosine_similarity_unit(self, a1, a2):
		#local variables & initialization
		a1_size = len(a1[0].get_similarities())
		a2_size = len(a2[0].get_similarities())
		
		#make output file
		output = prepare_output(self.path, "similarity_unit")
		
		#make title
		title = []
		for i in range(0, len(a1)):
			if a1[i].slot != a2[i].slot:
				raise RuntimeError("unexpected")
			title.append("similarity_1(" + str(a1[i].slot) + ")")
			title.append("similarity_2(" + str(a2[i].slot) + ")")
			
		#make data
		data = []
		maxlen = 0
		for i in range(0, len(a1)):
			if maxlen < len(a1[i].get_similarities()):
				maxlen = len(a1[i].get_similarities())
		for i in range(0, len(a2)):
			if maxlen < len(a2[i].get_similarities()):
				maxlen = len(a2[i].get_similarities())
		
		for i in range(0, maxlen):
			element = []
			for j in range(0, len(a1)):
				pushed = False
				try:
					element.append(a1[j].get_similarities()[i])
					pushed = True
				except IndexError:
					element.append(None)
					
				try:
					element.append(a2[j].get_similarities()[i])
				except IndexError:
					if pushed:
						element.pop()
						element.append(None)
					element.append(None)

			data.append(element)
			
		#make csv
		write_csv(output, title, data)
		
	def dump_cosine_similarity_std(self, a1, a2):
		#validation
		if len(a1) != len(a2):
			raise RuntimeError("unexpected")
		for i in range(0, len(a1)):
			if a1[i].slot != a2[i].slot:
				raise RuntimeError("unexpected")
				
		#make output
		output = prepare_output(self.path, "similarity_std")
			
		#make title
		title = [ "unit", "1", "2" ]
		
		#make data
		data = []
		for i in range(0, len(a1)):
			data.append([a1[i].slot, a1[i].get_std(), a2[i].get_std()])
			
		#make csv
		write_csv(output, title, data)
		
	def dump_point_similarity(self, a1, a2):
		#make output
		output = prepare_output(self.path, "point_similarity")
		
		#make title
		title = ["1", "2"]
		
		#set data range
		minlen = len(a1.similarities)
		if minlen > len(a2.similarities):
			minlen = len(a2.similarities)
		
		#make data
		data = []
		for i in range(0, minlen):
			data.append([a1.similarities[i], a2.similarities[i]])
			
		#make csv
		write_csv(output, title, data)
		
		#print additional information
		print ("1(std) : " + str(a1.get_std()))
		print ("2(std) : " + str(a2.get_std()))
		
	def dump_point_similarity_depend_slots(self, a1, a2):
		#make output
		output = prepare_output(self.path, "point_similarity_base_slot")
		
		#make title
		title = []
		for i in range(0, len(a1)):
			title.append(str(a1[i].area) + "(" + str(a1[i].slot) + ")_1")
			title.append(str(a1[i].area) + "(" + str(a1[i].slot) + ")_2")
			
		#set max height
		maxheight = 0
		for i in range(0, len(a1)):
			if maxheight < len(a1[i].similarities):
				maxheight = len(a1[i].similarities)
		for i in range(0, len(a2)):
			if maxheight < len(a2[i].similarities):
				maxheight = len(a2[i].similarities)
				
		#make data
		data = []
		for i in range(0, maxheight):
			element = []
			for j in range(0, len(a1)):
				if (i >= len(a1[j].similarities)) or (i >= len(a2[j].similarities)):
					element.append(None)
					element.append(None)
				else:
					element.append(a1[j].similarities[i])
					element.append(a2[j].similarities[i])
			data.append(element)
			
		#write csv
		write_csv(output, title, data)
		
	def dump_point_similarity_depend_slots_std(self, a1, a2):
		#make output
		output = prepare_output(self.path, "point_similarity_base_slot_std")
			
		#make title
		title = [ "unit", "1", "2" ]
		
		#make data
		data = []
		for i in range(0, len(a1)):
			data.append([str(a1[i].area) + "(" + str(a1[i].slot) + ")", \
				a1[i].get_std(), a2[i].get_std()])

		#make csv
		write_csv(output, title, data)
		
	def prepare_interval_distribution(self, a, name):
		#make title
		title = [ "interval_" + name, "value_" + name ]
		
		#process data
		r = a.get_interval_distribution()
		intervals = list(r.keys())
		intervals.sort()
		
		#make data
		data = []
		for i in range(0, len(intervals)):
			data.append([intervals[i], r[intervals[i]]])
		
		return title, data
		
	def prepare_interval_distribution_with_same_coord(self, a, name):
		r = a.get_interval_distribution_with_same_coord()
		
	def prepare_region(self, a, size_x, size_y, info):
		self.title = [ "region(" + str(size_x) + ", " + str(size_y) + ")_" + info ]
		self.data = []
		
		for i in range(0, len(a.nodes)):
			self.data.append([a.nodes[i].region])
			
	def prepare_region_distance(self, a, size_x, size_y, info):
		self.title = [ "region_distance(" + str(size_x) + ", " + str(size_y) + ")_" + info ]
		self.data = []
		
		for i in range(0, len(a.nodes)):
			self.data.append([a.nodes[i].region_distance])
			
	def prepare_region_direction(self, a, size_x, size_y, info):
		self.title = [ "region_direction(" + str(size_x) + ", " + str(size_y) + ")_" + info ]
		self.data = []
		
		for i in range(0, len(a.nodes)):
			self.data.append([a.nodes[i].region_direction])

	def merge(self, src):
		t = src.title
		d = src.data

		emptyE = []
		for i in range(0, len(self.data[0])):
			emptyE.append(None)

		self.title.extend(t)
		if len(self.data) >= len(d):
			for i in range(0, len(d)):
				self.data[i].extend(d[i])
			for i in range(len(d), len(self.data)):
				self.data[i].extend(emptyE)
		else:
			for i in range(0, len(self.data)):
				self.data[i].extend(d[i])
			for i in range(len(self.data), len(d)):
				newE = emptyE
				newE.extend(d)
				self.data.append(newE)
	
	def write(self, name):
		output = prepare_output(self.path, name)
		write_csv(output, self.title, self.data)
				
			
		
		
		
			
		
		
					
		
			
