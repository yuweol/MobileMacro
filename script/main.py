#!/usr/bin/env python

import sys

from yuweol_raw import Raw
from analyzer import Analyzer

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

def main():
	if not len(sys.argv) is 3:
		print ("[usage] python log.py ${log_file} ${log_file}")
		sys.exit(1)

	region_size = 9
	time_slot = 10
	max_budget = 200

	r1 = Raw(sys.argv[1])
	r2 = Raw(sys.argv[2])

        def linear_recover(x):
            return x+1
        def exp_recover(x):
            if x == 0:
                return 1
            else:
                return x*2

        a = Analyzer(RESULT_DIR)
        a.touch_density(time_slot, r1, "bot", r2, "human")
        a.touch_activation(time_slot, r1, "bot", r2, "human")
        a.score_rest(time_slot, linear_recover, r1, "bot", r2, "human")
        a.budget(time_slot, max_budget, exp_recover, r1, "bot", r2, "human")

if __name__ == "__main__":
	main()

#LEFT0 RIGHT8000 UP0 DOWN8000
