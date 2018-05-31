import sys

from yuweol_raw import Raw
from dumper import dumper
from analyzer import FrequencyAnalyzer
from analyzer import SelfSimilarityAnalyzer
from analyzer import CoordAnalyzer
from analyzer import PointSimilarityAnalyzer
from analyzer import Analyzer

def analyze_by_coord(v1, v2):
	area = 1
	coordAnalyzer_1 = CoordAnalyzer(v1)
	coordAnalyzer_1.analyze_by_area(area)
	coordAnalyzer_2 = CoordAnalyzer(v2)
	coordAnalyzer_2.analyze_by_area(area)
	
	dumper(".").dump_coord(coordAnalyzer_1, coordAnalyzer_2)
	
def analyze_by_frequency_area(v1, v2):
	areas = [ 1, 8, 64, 128, 256, 512, 1024, 2048 ]
	a1 = []
	a2 = []
	
	for i in range(0, len(areas)):
		s1 = FrequencyAnalyzer(v1, areas[i])
		s2 = FrequencyAnalyzer(v2, areas[i])
		s1.analyze()
		s2.analyze()
		a1.append(s1)
		a2.append(s2)
		
	dumper(".").dump_frequency_area(a1, a2)	
	
def analyze_by_cosine(v1, v2):
	time_slot = 600
	click_slot = 500
	cosineAnalyzer_1 = SelfSimilarityAnalyzer(v1, click_slot)
	cosineAnalyzer_1.analyze_by_click()
	
	cosineAnalyzer_2 = SelfSimilarityAnalyzer(v2, click_slot)
	cosineAnalyzer_2.analyze_by_click()
	
	dumper(".").dump_cosine_similarity(cosineAnalyzer_1, cosineAnalyzer_2)
	
	print ("1(std) : " + str(cosineAnalyzer_1.get_std()))
	print ("1(avg) " + str(cosineAnalyzer_1.get_average()))
	
	print ("2(std) : " + str(cosineAnalyzer_2.get_std()))	
	print ("2(avg) : " + str(cosineAnalyzer_2.get_average()))
	
def analyze_by_cosine_click_unit(v1, v2):
	click_slots = [ 10, 20, 30, 40, 50 ]
	a1 = []
	a2 = []
	for i in range(0, len(click_slots)):
		c1 = SelfSimilarityAnalyzer(v1, click_slots[i])
		c2 = SelfSimilarityAnalyzer(v2, click_slots[i])
		c1.analyze_by_click()
		c2.analyze_by_click()
		a1.append(c1)
		a2.append(c2)
		
	dumper(".").dump_cosine_similarity_unit(a1, a2)
	dumper(".").dump_cosine_similarity_std(a1, a2)
	
	for i in range(0, len(click_slots)):
		print ("[1](" + str(click_slots[i]) + ") avg : " + str(a1[i].get_average()) + ", std : " + \
			str(a1[i].get_std()) + ")")
		print ("[2](" + str(click_slots[i]) + ") avg : " + str(a2[i].get_average()) + ", std : " + \
			str(a2[i].get_std()) + ")")
			
def point_similarity(v1, v2):
	area = 2048
	slot = 40
	p1 = PointSimilarityAnalyzer(v1, area, slot)
	p2 = PointSimilarityAnalyzer(v2, area, slot)
	p1.analyze()
	p2.analyze()
	
	dumper(".").dump_point_similarity(p1, p2)
	
def point_similarity_depends_slots(v1, v2):
	slots = [ 10, 20, 30, 40, 50, 60, 70, 80, 90, 100 ]
	area = 2048
	
	a1 = []
	a2 = []
	for slot in slots:
		p1 = PointSimilarityAnalyzer(v1, area, slot)
		p2 = PointSimilarityAnalyzer(v2, area, slot)
		p1.analyze()
		p2.analyze()
		a1.append(p1)
		a2.append(p2)
		
	dumper(".").dump_point_similarity_depend_slots(a1, a2)
	dumper(".").dump_point_similarity_depend_slots_std(a1, a2)
	
def analyze(v1, v2):
	a1 = Analyzer(v1)
	a2 = Analyzer(v2)
	
	a1.set_region_label()
	a2.set_region_label()
	
	#r1 = dumper(".").prepare_interval_distribution_with_same_coord(a1, "bot")
	#r2 = dumper(".").prepare_interval_distribution_with_same_coord(a2, "human")
	
	#t1, d1 = dumper(".").prepare_interval_distribution(a1, "bot")
	#t2, d2 = dumper(".").prepare_interval_distribution(a2, "human")
	
	#dumper(".").dumps(t1, d1, t2, d2, "interval")
	
def test1(r1, r2):
	size_x = 20
	size_y = 20

	a1 = Analyzer(r1)
	a2 = Analyzer(r2)
	
	a1.normalize_burst_touch(1)
	a2.normalize_burst_touch(1)
	
	a1.set_region_label(size_x, size_y)
	a2.set_region_label(size_x, size_y)
	
	d = dumper(".")
	d.prepare_region(a1, size_x, size_y, "bot")
	
	td1 = dumper(".")
	td1.prepare_region_distance(a1, size_x, size_y, "bot")
	
	td2 = dumper(".")
	td2.prepare_region_direction(a1, size_x, size_y, "bot")
	
	td3 = dumper(".")
	td3.prepare_region(a2, size_x, size_y, "human")
	
	td4 = dumper(".")
	td4.prepare_region_distance(a2, size_x, size_y, "human")
	
	td5 = dumper(".")
	td5.prepare_region_direction(a2, size_x, size_y, "human")
	
	d.merge(td1)
	d.merge(td2)
	d.merge(td3)
	d.merge(td4)
	d.merge(td5)
	d.write("region")
	
def main():
	if not len(sys.argv) is 3:
		print ("[usage] python log.py ${log_file} ${log_file}")
		sys.exit(1)
		
	r1 = Raw(sys.argv[1])
	r2 = Raw(sys.argv[2])
	
	test1(r1, r2)
	
	#analyze_by_frequency_area(vectors_1, vectors_2)	
	#analyze_by_coord(vectors_1, vectors_2)
	#analyze_by_cosine(vectors_1, vectors_2)
	#analyze_by_cosine_click_unit(vectors_1, vectors_2)
	#point_similarity(vectors_1, vectors_2)
	#point_similarity_depends_slots(vectors_1, vectors_2)
	
	#analyze(vectors_1, vectors_2)
	
	
	"""	

	
	sys.exit(0)
	"""	
	"""
	
	min = vectors_1.size()
	if min > vectors_2.size():
		min = vectors_2.size()
	vectors_1.shrink(min)
	vectors_2.shrink(min)

	acc_data = []
	area = 10000
	for i in range(0, 5):		
		frequency_1 = FrequencyAnalyzer(vectors_1).get_approximate_frequency_information(area)
		frequency_2 = FrequencyAnalyzer(vectors_2).get_approximate_frequency_information(area)
		for j in range(0, len(frequency_1)):
			frequency_1[j] = (frequency_1[j][0] - frequency_2[j][0], frequency_1[j][1] - frequency_2[j][1])
		acc_data.append((area, frequency_1))
		area = int(area / 5)
	dumper(".").dump_frequency_diffs(acc_data)
	
	
	
	sys.exit(0)
	"""
		
	
	
	#dumper(".").dump_time_coordsum(vectors)
	
	#new_vectors = vector_manager()
	#for i in range(4094, 5138):
	#	new_vectors.append(vectors.get(i))
		
	#print (new_vectors.size())
		
	#dumper(".").dump_time_coordsum(new_vectors)
	
	#analyzer = miner()
	#top_score = analyzer.best_similarity(vectors)	
	#print ("top_score : similarity : " + str(top_score[0]) + " (" + str(top_score[1]) + " ~ " + str(top_score[2]) + ")")
	
if __name__ == "__main__":
	main()
	
#LEFT0 RIGHT8000 UP0 DOWN8000