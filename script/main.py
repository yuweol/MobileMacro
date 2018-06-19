#!/usr/bin/env python

import sys, os

from yuweol_raw import Raw
from analyzer import Analyzer
from config import Config

RESULT_DIR="result"

"""
def similarity(tg, activations, min_touch, size_x, size_y):
	similarities = []
	base_vector = [1,] * (size_x * size_y)

	for i in range(0, len(activations)):
		if activations[i] == 1 and len(tg.nodes[i].nodes) >= min_touch:
			vector = tg.nodes[i].vector(size_x, size_y)
			similarities.append(float(1.0 - spatial.distance.cosine(vector, base_vector)))
		else:
			similarities.append(0.0)

	return similarities

def draw_similarities_only_activated(time_slot, min_touch, regionSize, r1, r1_type, r2, r2_type):

	r1.setRegion(regionSize, regionSize)
	r2.setRegion(regionSize, regionSize)

	tg1 = TimeCluster(r1, time_slot)
	tg2 = TimeCluster(r2, time_slot)

	x1, y1 = tg1.density()
	x2, y2 = tg2.density()

	x1, y1, x2, y2 = shrink(x1, y1, x2, y2)

	ma1 = moving_average(y1)
	ma2 = moving_average(y2)

	a1 = activation(y1, ma1)
	a2 = activation(y2, ma2)

	s1 = similarity(tg1, a1, min_touch, regionSize, regionSize)
	s2 = similarity(tg2, a2, min_touch, regionSize, regionSize)

	t1 = Chart.trace_generator(x1, s1, "lines", r1_type + "_similarity")
	t2 = Chart.trace_generator(x2, s2, "lines", r2_type + "_similarity")

	filepath = RESULT_DIR + os.sep + "similarity(" + str(time_slot) + ").html"
	Chart.draw_simpleLine(filepath, [t1, t2])
"""

infos = [ ("FM", 5, 5, "data_fm", "4b00", "2b00"), ("COC", 5, 1, "data_coc", "8000", "8000") ]

def main():
#	max_budget = 30
	for info in infos:
		game, region_size, time_slot, data_dir, Config.max_x, Config.max_y = info

		bot_files = []
		human_files = []
		files = os.listdir(data_dir)
		for i in range(0, len(files)):
			if "_bot_" in files[i]:
				bot_files.append(data_dir + os.sep + files[i])
			elif "_human_" in files[i]:
				human_files.append(data_dir + os.sep + files[i])

		print "[Below bot files were found.]"
		for i in range(0, len(bot_files)):
			print "\t- " + bot_files[i]
		print "\n[Below human files were found.]"
		for i in range(0, len(human_files)):
			print "\t- " + human_files[i]

		botRaws = []
		humanRaws = []
		for i in range(0, len(bot_files)):
			botRaws.append(Raw(bot_files[i]))
			botRaws[-1].setRegion(region_size, region_size)
		for i in range(0, len(human_files)):
			humanRaws.append(Raw(human_files[i]))
			humanRaws[-1].setRegion(region_size, region_size)

		def linear_recover(x):
			return x+1
		def exp_recover(x):
			if x == 0:
				return 1
			else:
				return x*3

		a = Analyzer(RESULT_DIR)
	#	a.touch_density(time_slot, botRaws, humanRaws)
	#	a.touch_activation(time_slot, botRaws, humanRaws)
	#	a.score_rest(time_slot, linear_recover, botRaws, humanRaws)
	#	a.budget(time_slot, max_budget, linear_recover, botRaws, humanRaws)
	#	a.shift(time_slot, botRaws, humanRaws)
	#	a.actRatio(time_slot, [botRaws[0],], [humanRaws[0],])
	#	a.actChanges(time_slot, [botRaws[0]], [humanRaws[0]])
#		a.restRatio(game, time_slot, botRaws, humanRaws)
	#	a.distributionAnalyzer(time_slot, botRaws, humanRaws)
		a.regionAnalyzerByTime(game, botRaws[0])
#		a.regionAnalyzerByContinuous(game, time_slot, botRaws, humanRaws)
#		a.regionSimilarityByContinuous(game, time_slot, region_size, botRaws, humanRaws)
	#	a.actSeqNum(time_slot, [botRaws[1]], [humanRaws[2]])
	#	a.regionSimilarityByTime(time_slot, time_slot, region_size, botRaws, humanRaws)
#		a.mixedFeature(time_slot, region_size, botRaws, humanRaws)
#		a.restTimeDistribution(game, time_slot, botRaws, humanRaws)
	#	a.restSimOverTime(time_slot, botRaws, humanRaws)
	#	a.touchSimOverTime(time_slot, region_size, botRaws, humanRaws)
	
if __name__ == "__main__":
	main()

#LEFT0 RIGHT8000 UP0 DOWN8000
