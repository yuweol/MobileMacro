#!/usr/bin/env python

import sys, os

from yuweol_raw import Raw
from dumper import dumper
from cluster import TimeCluster
from chart import Chart
from scipy import spatial

RESULT_DIR="result"

def touch_density(r1, r2, time_slot):
	tg1 = TimeCluster(r1, time_slot)
	x1, y1 = tg1.density()

	tg2 = TimeCluster(r2, time_slot)
	x2, y2 = tg2.density()

	if len(x1) > len(x2):
		x1 = x1[:len(x2)]
		y1 = y1[:len(x2)]
	else:
		x2 = x2[:len(x1)]
		y2 = y2[:len(x1)]

	a1 = float("{0:.2f}".format(float(sum(y1))/float(len(y1))))
	a2 = float("{0:.2f}".format(float(sum(y2))/float(len(y2))))
	ya1 = []
	for i in range(0, len(y1)):
		ya1.append(float("{0:.2f}".format(float(sum(y1[:i+1]))/float(i+1))))
	ya2 = []
	for i in range(0, len(y2)):
		ya2.append(float("{0:.2f}".format(float(sum(y2[:i+1]))/float(i+1))))

	t1 = Chart.trace_generator(x1, y1, "lines", "bot")
	t2 = Chart.trace_generator(x1, ya1, "lines", "bot_average")
	t3 = Chart.trace_generator(x2, y2, "lines", "human")
	t4 = Chart.trace_generator(x2, ya2, "line", "human_average")
	
	filepath = RESULT_DIR + os.sep + "density(" + str(time_slot) + \
		").html"
	Chart.draw_simpleLine(filepath, [t1, t2, t3, t4])

def touch_density_above_average(r1, r2, time_slot):
	tg1 = TimeCluster(r1, time_slot)
	x1, y1 = tg1.density()

	tg2 = TimeCluster(r2, time_slot)
	x2, y2 = tg2.density()

	if len(x1) > len(x2):
		x1 = x1[:len(x2)]
		y1 = y1[:len(x2)]
	else:
		x2 = x2[:len(x1)]
		y2 = y2[:len(x1)]

	a1 = float("{0:.2f}".format(float(sum(y1))/float(len(y1))))
	a2 = float("{0:.2f}".format(float(sum(y2))/float(len(y2))))
	ya1 = []
	for i in range(0, len(y1)):
		ya1.append(float("{0:.2f}".format(float(sum(y1[:i+1]))/float(i+1))))
	ya2 = []
	for i in range(0, len(y2)):
		ya2.append(float("{0:.2f}".format(float(sum(y2[:i+1]))/float(i+1))))

	for i in range(0, len(y1)):
		if y1[i] < ya1[i]:
			y1[i] = 0.0
	for i in range(0, len(y2)):
		if y2[i] < ya2[i]:
			y2[i] = 0.0

	t1 = Chart.trace_generator(x1, y1, "lines", "bot")
	t2 = Chart.trace_generator(x1, ya1, "lines", "bot_average")
	t3 = Chart.trace_generator(x2, y2, "lines", "human")
	t4 = Chart.trace_generator(x2, ya2, "line", "human_average")
	
	filepath = RESULT_DIR + os.sep + "density(" + str(time_slot) + \
		").html"
	Chart.draw_simpleLine(filepath, [t1, t2, t3, t4])

def rest_time_counter(r1, r2, time_slot, zero=True):
	tg1 = TimeCluster(r1, time_slot)
	x1, y1 = tg1.density()

	tg2 = TimeCluster(r2, time_slot)
	x2, y2 = tg2.density()

	if len(x1) > len(x2):
		x1 = x1[:len(x2)]
		y1 = y1[:len(x2)]
	else:
		x2 = x2[:len(x1)]
		y2 = y2[:len(x1)]

	a1 = float("{0:.2f}".format(float(sum(y1))/float(len(y1))))
	a2 = float("{0:.2f}".format(float(sum(y2))/float(len(y2))))

	if zero == False:
		ya1 = []
		for i in range(0, len(y1)):
			ya1.append(float("{0:.2f}".format(float(sum(y1[:i+1]))/float(i+1))))
		ya2 = []
		for i in range(0, len(y2)):
			ya2.append(float("{0:.2f}".format(float(sum(y2[:i+1]))/float(i+1))))

		c1 = [1]
		for i in range(1, len(y1)):
			if y1[i] < ya1[i]:
				c1.append(c1[i-1]+1)
			else:
				c1.append(c1[i-1])
		c2 = [1]
		for i in range(1, len(y2)):
			if y2[i] < ya2[i]:
				c2.append(c2[i-1]+1)
			else:
				c2.append(c2[i-1])
		title = "rest_time_average"
	else:
		c1 = [0]
		for i in range(0, len(y1)):
			if y1[i] == 0:
				c1.append(c1[i]+1)
			else:
				c1.append(c1[i])
		c1 = c1[1:]

		c2 = [0]
		for i in range(0, len(y2)):
			if y2[i] == 0:
				c2.append(c2[i]+1)
			else:
				c2.append(c2[i])
		c2 = c2[1:]
		title = "rest_time_zero"

	t1 = Chart.trace_generator(x1, c1, "lines", "bot_" + title)
	t2 = Chart.trace_generator(x2, c2, "lines", "human_" + title)
	
	filepath = RESULT_DIR + os.sep + title + "(" + str(time_slot) + \
		").html"
	Chart.draw_simpleLine(filepath, [t1, t2])

def density(r, time_slot):
	tg = TimeCluster(r, time_slot)
	return tg.density()

def shrink(x1, y1, x2, y2):
	if len(x1) > len(x2):
		x1 = x1[:len(x2)]
		y1 = y1[:len(y2)]
	else:
		x2 = x2[:len(x1)]
		y2 = y2[:len(y1)]
	return x1, y1, x2, y2

def moving_average(y):
	ma = []
	for i in range(0, len(y)):
		ma.append(float("{0:.2f}".format(float(sum(y[:i+1]))/float(i+1))))
	return ma

def activation(y, ma):
	a = []
	for i in range(0, len(ma)):
		if y[i] >= ma[i]:
			a.append(1)
		else:
			a.append(0)
	return a

def similarity(tg, activations, min_touch, size_x, size_y):
	similarities = []
	base_vector = [1,] * (size_x * size_y)

	for i in range(0, len(activations)):
		if activations[i] == 1 and len(tg.nodes[i].nodes) >= min_touch:
			vector = tg.nodes[i].vector(size_x, size_y)
			similarities.append(float(1.0 - spatial.distance.cosine(vector, base_vector)))
			print base_vector
		else:
			similarities.append(0.0)

	return similarities

def draw_activates(time_slot, r1, r1_type, r2, r2_type):
	x1, y1 = density(r1, time_slot)
	x2, y2 = density(r2, time_slot)

	x1, y1, x2, y2 = shrink(x1, y1, x2, y2)

	ma1 = moving_average(y1)
	ma2 = moving_average(y2)

	a1 = activation(y1, ma1)
	a2 = activation(y2, ma2)

	t1 = Chart.trace_generator(x1, a1, "lines", r1_type + "_activation")
	t2 = Chart.trace_generator(x2, a2, "lines", r2_type + "_activation")
	
	filepath = RESULT_DIR + os.sep + "activation(" + str(time_slot) + ").html"
	Chart.draw_simpleLine(filepath, [t1, t2])

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

def score_continuous_rest_time(r1, r2, time_slot, zero=True):
	tg1 = TimeCluster(r1, time_slot)
	x1, y1 = tg1.density()

	tg2 = TimeCluster(r2, time_slot)
	x2, y2 = tg2.density()

	if len(x1) > len(x2):
		x1 = x1[:len(x2)]
		y1 = y1[:len(x2)]
	else:
		x2 = x2[:len(x1)]
		y2 = y2[:len(x1)]

	a1 = float("{0:.2f}".format(float(sum(y1))/float(len(y1))))
	a2 = float("{0:.2f}".format(float(sum(y2))/float(len(y2))))

	if zero == False:
		ya1 = []
		for i in range(0, len(y1)):
			ya1.append(float("{0:.2f}".format(float(sum(y1[:i+1]))/float(i+1))))
		ya2 = []
		for i in range(0, len(y2)):
			ya2.append(float("{0:.2f}".format(float(sum(y2[:i+1]))/float(i+1))))

		budget = 1
		c1 = [1]
		for i in range(1, len(y1)):
			if y1[i] < ya1[i]:
				c1.append(c1[i-1]+budget)
				budget += 1
			else:
				c1.append(c1[i-1])
				budget = 1
		budget = 1
		c2 = [1]
		for i in range(1, len(y2)):
			if y2[i] < ya2[i]:
				c2.append(c2[i-1]+budget)
				budget += 1
			else:
				c2.append(c2[i-1])
				budget = 1
		title = "score_average"
	else:
		budget = 1
		c1 = [0]
		for i in range(0, len(y1)):
			if y1[i] == 0:
				c1.append(c1[i]+1)
				budget *= 2
			else:
				c1.append(c1[i])
				budget = 1
		c1 = c1[1:]

		budget = 1
		c2 = [0]
		for i in range(0, len(y2)):
			if y2[i] == 0:
				c2.append(c2[i]+1)
				budget *= 2
			else:
				c2.append(c2[i])
				budget = 1
		c2 = c2[1:]
		title = "score_zero"

	t1 = Chart.trace_generator(x1, c1, "lines", "bot_" + title)
	t2 = Chart.trace_generator(x2, c2, "lines", "human_" + title)
	
	filepath = RESULT_DIR + os.sep + title + "(" + str(time_slot) + \
		").html"
	Chart.draw_simpleLine(filepath, [t1, t2])

def budget_analysis(value, average, max_budget):
	#1. Constant budget analysis
	constant_budgets = [ max_budget, ] * len(value)
	for i in range(0, len(value)):
		constant_budgets[i] -= value[i]

	#2. Flexible budget based on rest time
	flexible_budgets = [ max_budget, ]
	recovery_factor = 0
	for i in range(1, len(value)):
		flexible_budgets.append(flexible_budgets[i-1] - value[i-1] + recovery_factor)
		if flexible_budgets[-1] >= max_budget:
			flexible_budgets[-1] = max_budget
		if value[i-1] > average[i-1]:
			if recovery_factor == 0:
				recovery_factor = 1
			else:
				recovery_factor *= 2
			if recovery_factor >= max_budget:
				recovery_factor = max_budget
		else:
			recovery_factor = 0

	return constant_budgets, flexible_budgets


def budget_test(r1, r2, time_slot, max_budget, zero=True):
	tg1 = TimeCluster(r1, time_slot)
	x1, y1 = tg1.density()

	tg2 = TimeCluster(r2, time_slot)
	x2, y2 = tg2.density()

	if len(x1) > len(x2):
		x1 = x1[:len(x2)]
		y1 = y1[:len(x2)]
	else:
		x2 = x2[:len(x1)]
		y2 = y2[:len(x1)]

	a1 = float("{0:.2f}".format(float(sum(y1))/float(len(y1))))
	a2 = float("{0:.2f}".format(float(sum(y2))/float(len(y2))))

	if zero == False:
		ya1 = []
		for i in range(0, len(y1)):
			ya1.append(float("{0:.2f}".format(float(sum(y1[:i+1]))/float(i+1))))
		ya2 = []
		for i in range(0, len(y2)):
			ya2.append(float("{0:.2f}".format(float(sum(y2[:i+1]))/float(i+1))))

		budget = 1
		c1 = [1]
		for i in range(1, len(y1)):
			if y1[i] < ya1[i]:
				c1.append(c1[i-1]+budget)
				budget += 1
			else:
				c1.append(c1[i-1])
				budget = 1
		budget = 1
		c2 = [1]
		for i in range(1, len(y2)):
			if y2[i] < ya2[i]:
				c2.append(c2[i-1]+budget)
				budget += 1
			else:
				c2.append(c2[i-1])
				budget = 1
		base = "_average"
	else:
		budget = 1
		c1 = [0]
		for i in range(0, len(y1)):
			if y1[i] == 0:
				c1.append(c1[i]+1)
				budget *= 2
			else:
				c1.append(c1[i])
				budget = 1
		c1 = c1[1:]

		budget = 1
		c2 = [0]
		for i in range(0, len(y2)):
			if y2[i] == 0:
				c2.append(c2[i]+1)
				budget *= 2
			else:
				c2.append(c2[i])
				budget = 1
		c2 = c2[1:]
		base += "_zero"

	cb1, fb1 = budget_analysis(y1, ya1, max_budget)
	cb2, fb2 = budget_analysis(y2, ya2, max_budget)
	t1 = Chart.trace_generator(x1, cb1, "lines", "bot_constant_budget_" + base)
	t2 = Chart.trace_generator(x1, fb1, "lines", "bot_flexible_budget_" + base)
	t3 = Chart.trace_generator(x1, cb2, "lines", "human_constant_budget_" + base)
	t4 = Chart.trace_generator(x1, fb2, "lines", "human_flexible_budget_" + base)

	filepath = RESULT_DIR + os.sep + base + "(" + str(time_slot) + \
		").html"
	Chart.draw_simpleLine(filepath, [t1, t2, t3, t4])

def main():
	if not len(sys.argv) is 3:
		print ("[usage] python log.py ${log_file} ${log_file}")
		sys.exit(1)

	region_size = 9
	min_touch = 10
	time_slot = 10
	max_budget = 200
		
	r1 = Raw(sys.argv[1])
	r2 = Raw(sys.argv[2])
	
	draw_similarities_only_activated(time_slot, min_touch, region_size, r1, "bot", r2, "human")
	touch_density(r1, r2, time_slot)
#	rest_time_counter(r1, r2, 10, zero=False)
	draw_activates(time_slot, r1, "bot", r2, "human")
	score_continuous_rest_time(r1, r2, time_slot, zero=False)
	budget_test(r1, r2, time_slot, max_budget, zero=False)
	
if __name__ == "__main__":
	main()
	
#LEFT0 RIGHT8000 UP0 DOWN8000
