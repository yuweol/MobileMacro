#!/usr/bin/env
from cluster import TimeCluster
from chart import Chart
from scipy import spatial

import os, numpy, distance, math

def clusteredDensity(time_slot, r):
    return TimeCluster(r, time_slot).density()

def groupClusteredDensity(time_slot, raws):
	clusters = []
	for i in range(0, len(raws)):
		clusters.append(TimeCluster(raws[i], time_slot).density())
	return clusters

def fitSize(lists, toMin = True):
	val = len(lists[0][0])
	for i in range(1, len(lists)):
		if (toMin) and (val > len(lists[i][0])):
			val = len(lists[i][0])
		elif (not toMin) and (val < len(lists[i][0])):
			val = len(lists[i][0])
	return val

def fit((x, y), size):
	if len(x) == size:
		return (x, y)
	elif len(x) > size:
		return (x[:size], y[:size])
	else:
		for i in range(0, size - len(x)):
			x.append(None)
			y.append(None)
	return x, y

def groupFit(size, src):
	for i in range(0, len(src)):
		src[i] = fit(src[i], size)
	return src

def movingAverage(y):
	ma = []
	for i in range(0, len(y)):
		ma.append(float("{0:.2f}".format(float(sum(y[:i+1]))/float(i+1))))
	return ma

def groupMovingAverage(src):
	mas = []
	for i in range(0, len(src)):
		mas.append(movingAverage(src[i][1]))
	return mas

def activation(y, ma):
    a = []
    for i in range(0, len(ma)):
#		if y[i] >= ma[i]:
		if y[i] > 0:
			a.append(1)
		else:
			a.append(0)
    return a

def groupActivation(src, mas):
	activities = []
	for i in range(0, len(src)):
		activities.append(activation(src[i][1], mas[i]))
	return activities

def score(a, fun):
    s = [1, ]
    factor = 1

    for i in range(1, len(a)):
        if a[i] == 1:
            s.append(s[-1] + factor)
            factor = fun(factor)
        else:
            s.append(s[-1])
            factor = 1

    return s

def groupScore(acts, fun):
	scores = []
	for i in range(0, len(acts)):
		scores.append(score(acts[i], fun))
	return scores

def budget(act, fun, maxBudget):
    b = [maxBudget, ]
    factor = 0

    for i in range(1, len(a)):
		next_budget = b[i-1] - act[i]
		if act[i] == act[i-1]:
			factor = fun(factor)
			if factor >= maxBudget:
				factor = maxBudget
			next_budget += factor
			if next_budget >= maxBudget:
				next_budget = maxBudget
		else:
			factor = 0
		b.append(next_budget)
    return b

def groupBudget(acts, fun, maxBudget):
	budgets = []
	for i in range(0, len(acts)):
		budgets.append(budget(acts[i], fun, maxBudget))
	return budgets

def continuous(clusters):
	c = []
	conact = 0
	conrst = 0
	conden = 0
	sTime = 0.0
	eTime = 0.0
	for i in range(0, len(clusters[0])):
		if clusters[1][i] < 1:
			if conact != 0:
				c.append(("A", conact, sTime, clusters[0][i], conden))
				conact = 0
				conden = 0
				sTime = clusters[0][i]
			conrst += 1
		else:
			if conrst != 0:
				c.append(("R", conrst, sTime, clusters[0][i], 0))
				conrst = 0
				sTime = clusters[0][i]
			conact += 1
			conden += clusters[1][i]
	return c

def groupContinuous(clusters):
	cons = []
	for i in range(0, len(clusters)):
		con = continuous(clusters[i])
		if con[0][0] == "R":
			con = con[1:]
		cons.append(con)
	return cons

#pCon structure : (Active Start, Active End, Rest Start, Rest End, Touch Num)
def pairContinuous(con):
	size = len(con)
	pcon = []
	if size % 2 != 0:
		con = con[:len(con)-1]

	i = 0
	while i < len(con):
		if len(con[i]) != 5:
			raise RuntimeError("Unexpected Node : (" + str(con[i]) + ")")
		pcon.append((con[i][2], con[i][3], con[i+1][2], con[i+1][3], con[i][4]))
		if con[i+1][4] != 0:
			print con[i+1]
			raise RuntimeError("Unexpected")
		if con[i][2] > con[i][3]:
			print con[i]
			raise RuntimeError("Unexpected")
		if con[i+1][2] > con[i+1][3]:
			print con[i+1]
			raise RuntimeError("Unexepected")

		"""
		if con[i][1] > con[i+1][1]:
			pcon.append((con[i][0], con[i][1], con[i+1][1]))
		elif con[i][1] < con[i+1][1]:
			pcon.append((con[i+1][0], con[i+1][1], con[i][1]))
		elif con[i][1] == con[i+1][1]:
			pcon.append(("A", con[i][1], con[i+1][1]))
		"""

		i += 2
	return pcon

def groupPairContinuous(cons):
	pcons = []
	for i in range(0, len(cons)):
		pcons.append(pairContinuous(cons[i]))
	return pcons

def actRatio(pCon, timeSlot):
	ratio = []
	for e in pCon:
		a = e[1] - e[0]
		r = e[3] - e[2]
#		ratio.append(float("{0:.2f}".format(float(a) / float(a+r))))
#		ratio.append(float(a) / float(e[4]))
#		ratio.append(float(a) / float(a+r))
#		ratio.append((float(r) / float(a+r), float(e[4]) / float(a+r), float(e[4]) / float(a)))
#		ratio.append((float(r) / float(a+r), float(a) / float(e[4])))
		ratio.append((float(r) / float(a+r)))
	return ratio

def groupActRatio(pCons, timeSlot):
	groupRatio = []
	for pCon in pCons:
		groupRatio.append(actRatio(pCon, timeSlot))
	return groupRatio

def activitiesBasedOnTime(clusters, acts):
	activities = []
	for i in range(0, len(clusters[0])):
		con = continuous(clusters[:i+1], acts[:i+1])
		pcon = pairContinuous(con)
		activities.append(len(pcon))
	return activities

def groupActivitiesBasedOnTime(clusters, acts):
	ret = []
	for i in range(0, len(clusters)):
		ret.append(activitiesBasedOnTime(clusters[i], acts[i]))
	return ret

#TO BE DELETED
def getActRatios(timeSlot, raws):
	clusters = groupClusteredDensity(timeSlot, raws)
	cons = groupContinuous(clusters)
	pairCons = groupPairContinuous(cons)
	return groupActRatio(pairCons, timeSlot)

def restRatioSimilarities(timeSlot, raws):
	densities = groupClusteredDensity(timeSlot, raws)
	cons = groupContinuous(densities)
	pairCons = groupPairContinuous(cons)
	rateRatios = groupActRatio(pairCons, timeSlot)
	rateSimilarities = []
	for e in rateRatios:
		rateSimilarities.append(actRatioSimilarity(e))
	return rateSimilarities

def getTimeContinuous(con):
	result = []
	i = 0
	while i < len(con) - 1:
		sTime = con[i][3]
		try:
			eTime = con[i+2][3]
		except IndexError:
			eTime = con[i+1][3] + 1
		result.append((sTime, eTime))
		i += 2
	return result

def getTimeContinuousesFromClusters(clusters):
	result = []
	densities = []
	for cluster in clusters:
		densities.append(cluster.density())
	cons = groupContinuous(densities)
	for con in cons:
		result.append(getTimeContinuous(con))
	return result

def getTimeContinuouses(timeSlot, raws):
	clusters = []
	for raw in raws:
		clusters.append(TimeCluster(raw, timeSlot))
	return getTimeContinuousesFromClusters(clusters)

def getRegionVector(regionSize, cluster, sTime, eTime):
	result = []
	try:
		touches = cluster.getTouches(sTime, eTime)
	except IndexError:
		print "sTime : " + str(sTime) + ", eTime : " + str(eTime)
		sys.exit(0)
	actualTouches = []
	for touch in touches:
		for e in touch:
			actualTouches.append(e)
	vector = [0] * (regionSize * regionSize)
	for touch in actualTouches:
		vector[touch.region] += 1
	return vector

def getRegionVectorByTime(regionSize, cluster, cons):
	result = []
	for i in range(0, len(cons)):
		vector = getRegionVector(regionSize, cluster, cons[i][0], cons[i][1])
		result.append(vector)
	return result

def getRegionVectorByTimes(regionSize, clusters, cons):
	result = []
	if len(clusters) != len(cons):
		raise RuntimeError("invalid input")

	for i in range(0, len(cons)):
		result.append(getRegionVectorByTime(regionSize, clusters[i], cons[i]))
	return result

def getRegionSimilarity(regionSize, vectors):
	result = []
	unitvector = [0.0] * (regionSize * regionSize)
#	unitvector[regionSize * regionSize / 2] = 1.0
	for vector in vectors:
		if sum(vector) == 0.0:
			continue
		unitvector[regionSize * regionSize / 2] = float(sum(vector))
#		for i in range(0, len(unitvector)):
#			unitvector[i] = float(sum(vector)) / float(len(unitvector))
		distance = spatial.distance.cosine(unitvector, vector)
		if numpy.isnan(distance):
			raise RuntimeError(str(vector))
		similarity = 1.0 - distance
		result.append(similarity)
	return result

def getRegionSimilarities(regionSize, vectors):
	result = []
	for vector in vectors:
		result.append(getRegionSimilarity(regionSize, vector))
	return result

def getDistribution(actRatio, title):
	temp = {}
	for e in actRatio:
		try:
			temp[e] += 1
		except KeyError:
			temp[e] = 1
	x = temp.keys()
	x.sort()
	y = []
	for e in x:
		y.append(temp[e])
	z = title
	return x, y, z

def getDistributions(actRatios, title):
	result = []
	cnt = 1
	for actRatio in actRatios:
		result.append(getDistribution(actRatio, title + "(" + str(cnt) + ")"))
		cnt += 1
	return result

def getRegion(raw, title):
	x = []
	y = []
	z = title
	for e in raw.nodes:
		x.append(e.time)
		y.append(e.region)
	return x, y, z

def getRegions(raws, title):
	result = []
	cnt = 1
	for raw in raws:
		result.append(getRegion(raw, title + "(" + str(cnt) + ")"))
		cnt += 1
	return result

def getTimeClusters(timeSlot, raws):
	result = []
	for raw in raws:
		result.append(TimeCluster(raw, timeSlot))
	return result

def actRatioSimilarity(actRatio):
	for e in actRatio:
		try:
			if len(e) != 2:
				raise RuntimeError("Unexpected : " + str(e))
		except TypeError:
			return actRatio

	baseVector = [1.0, 1.0]
	result = []
	for e in actRatio:
		result.append(1.0 - spatial.distance.cosine(baseVector, [e]))

	return result

def getDeviations(srcs):
	stds = []
	for src in srcs:
		if len(src) == 0:
			raise RuntimeError("unexpected")
		stds.append(0.5 - numpy.std(src))
	return stds

def cosineSimilarity(srcs):
	results = []

	dimension = len(srcs)
	unitvector = [1.0] * dimension

	for i in range(0, len(srcs[0])):
		result = []
		for j in range(0, len(srcs[0][i])):
			vector = []
			for k in range(0, dimension):
				vector.append(srcs[k][i][j])
			distance = spatial.distance.cosine(unitvector, vector)
			similarity = 1.0 - distance
			result.append(similarity)
		results.append(result)
	return results

def shrink(bs, hs):
	minNum = -1
	for e in bs:
		if minNum == -1:
			minNum = len(e)
		elif minNum > len(e):
			minNum = len(e)
	for e in hs:
		if minNum > len(e):
			minNum = len(e)

	for i in range(0, len(bs)):
		bs[i] = bs[i][:minNum]
	for i in range(0, len(hs)):
		hs[i] = hs[i][:minNum]

	return bs, hs

def printPairContinuous(pCons):
	for i in range(0, len(pCons)):
		if pCons[i][0] == "A":
			print "Activated : " + str(pCons[i][1]) + ", Rest : " + str(pCons[i][2]) + ", actratio : " + "{0:.2f}".format(float(pCons[i][1]) / float(pCons[i][2]))
		else:
			print "Activated : " + str(pCons[i][2]) + ", Rest : " + str(pCons[i][1]) + ", actratio : " + "{0:.2f}".format(float(pCons[i][2]) / float(pCons[i][1]))

class Analyzer():
    def __init__(self, path):
        self.path = path

    def touch_density(self, time_slot, botRaws, humanRaws):
		botDensities = groupClusteredDensity(time_slot, botRaws)
		humanDensities = groupClusteredDensity(time_slot, humanRaws)

		botFitSize = fitSize(botDensities, toMin = True)
		humanFitSize = fitSize(humanDensities, toMin = True)
		minFitSize = botFitSize
		if minFitSize > humanFitSize:
			minFitSize = humanFitSize
		
		botDensities = groupFit(minFitSize, botDensities)	
		humanDensities = groupFit(minFitSize, humanDensities)

		data = []
		cnt = 1
		for cluster in botDensities:
			data.append((cluster[0], cluster[1], "bot(" + str(cnt) + ")"))
			cnt += 1
		cnt = 1
		for cluster in humanDensities:
			data.append((cluster[0], cluster[1], "human(" + str(cnt) + ")"))
			cnt += 1

		Chart.draw_line2("result/density.html", \
			data, "touchDensity", "time(s)", "NumberOfTouches")

    def touch_activation(self, time_slot, botRaws, humanRaws):
		botClusters = groupClusteredDensity(time_slot, botRaws)
		humanClusters = groupClusteredDensity(time_slot, humanRaws)

		botFitSize = fitSize(botClusters, toMin = True)
		humanFitSize = fitSize(humanClusters, toMin = True)
		minFitSize = botFitSize
		if minFitSize > humanFitSize:
			minFitSize = humanFitSize
		
		botClusters = groupFit(minFitSize, botClusters)	
		humanClusters = groupFit(minFitSize, humanClusters)

		botMA = groupMovingAverage(botClusters)
		humanMA = groupMovingAverage(humanClusters)

		botActs = groupActivation(botClusters, botMA)
		humanActs = groupActivation(humanClusters, humanMA)

		for i in range(0, len(botActs)):
			actcnt = 0
			concnt = 0
			conrst = 0
			for j in range(0, len(botActs[i])):
				if botActs[i][j] == 1:
					if conrst != 0:
						print "continuous rest (" + str(conrst) + ")"
					actcnt += 1
					concnt += 1
					conrst = 0
				else:
					if concnt != 0:
						print "continuous activated (" + str(concnt) + ")"
					concnt = 0
					conrst += 1
			print "bot(" + str(i+1) + ") - activated : " + str(actcnt) + "/" + str(len(botActs[i]))
		for i in range(0, len(humanActs)):
			actcnt = 0
			concnt = 0
			conrst = 0
			for j in range(0, len(humanActs[i])):
				if humanActs[i][j] == 1:
					if conrst != 0:
						print "continuous rest (" + str(conrst) + ")"
					actcnt += 1
					concnt += 1
					conrst = 0
				else:
					if concnt != 0:
						print "continuous activated (" + str(concnt) + ")"
					concnt = 0
					conrst += 1

			for j in range(0, len(humanActs[i])):
				if humanActs[i][j] == 1:
					actcnt += 1
			print "human(" + str(i+1) + ") - activated : " + str(actcnt) + "/" + str(len(humanActs[i]))

		sys.exit(0)

		t = []
		for i in range(0, len(botClusters)):
			t.append(Chart.trace_generator(botClusters[i][0], botActs[i], "lines", "bot(" + str(i+1) + ")_activation"))
		for i in range(0, len(humanClusters)):
			t.append(Chart.trace_generator(humanClusters[i][0], humanActs[i], "lines", "human(" + str(i+1) + ")_activation"))

		filepath = self.path + os.sep + "activation(" + str(time_slot) + ").html"
		Chart.draw_simpleLine(filepath, t)

    def score_rest(self, time_slot, fun, botRaws, humanRaws):
		botClusters = groupClusteredDensity(time_slot, botRaws)
		humanClusters = groupClusteredDensity(time_slot, humanRaws)

		botFitSize = fitSize(botClusters, toMin = True)
		humanFitSize = fitSize(humanClusters, toMin = True)
		minFitSize = botFitSize
		if minFitSize > humanFitSize:
			minFitSize = humanFitSize
		
		botClusters = groupFit(minFitSize, botClusters)	
		humanClusters = groupFit(minFitSize, humanClusters)

		botMA = groupMovingAverage(botClusters)
		humanMA = groupMovingAverage(humanClusters)

		botActs = groupActivation(botClusters, botMA)
		humanActs = groupActivation(humanClusters, humanMA)

		botScores = groupScore(botActs, fun)
		humanScores = groupScore(humanActs, fun)

		t = []
		for i in range(0, len(botClusters)):
			t.append(Chart.trace_generator(botClusters[i][0], botScores[i], "lines", "bot(" + str(i+1) + ")_score"))
		for i in range(0, len(humanClusters)):
			t.append(Chart.trace_generator(humanClusters[i][0], humanScores[i], "lines", "human(" + str(i+1) + ")_score"))

		filepath = self.path + os.sep + "score(" + str(time_slot) + ").html"
		Chart.draw_simpleLine(filepath, t)

    def budget(self, time_slot, max_budget, fun, botRaws, humanRaws):
		botClusters = groupClusteredDensity(time_slot, botRaws)
		humanClusters = groupClusteredDensity(time_slot, humanRaws)

		botFitSize = fitSize(botClusters, toMin = True)
		humanFitSize = fitSize(humanClusters, toMin = True)
		minFitSize = botFitSize
		if minFitSize > humanFitSize:
			minFitSize = humanFitSize
		
		botClusters = groupFit(minFitSize, botClusters)	
		humanClusters = groupFit(minFitSize, humanClusters)

		botMA = groupMovingAverage(botClusters)
		humanMA = groupMovingAverage(humanClusters)

		botActs = groupActivation(botClusters, botMA)
		humanActs = groupActivation(humanClusters, humanMA)

		botBudgets = groupBudget(botActs, botClusters, fun, max_budget)
		humanBudgets = groupBudget(humanActs, humanClusters, fun, max_budget)

		t = []
		for i in range(0, len(botClusters)):
			t.append(Chart.trace_generator(botClusters[i][0], botBudgets[i], "lines", "bot(" + str(i+1) + ")_budget"))
		for i in range(0, len(humanClusters)):
			t.append(Chart.trace_generator(humanClusters[i][0], humanBudgets[i], "lines", "human(" + str(i+1) + ")_budget"))

		filepath = self.path + os.sep + "budget(" + str(time_slot) + ").html"
		Chart.draw_simpleLine(filepath, t)

    def shift(self, time_slot, botRaws, humanRaws):
		botClusters = groupClusteredDensity(time_slot, botRaws)
		humanClusters = groupClusteredDensity(time_slot, humanRaws)

		botFitSize = fitSize(botClusters, toMin = True)
		humanFitSize = fitSize(humanClusters, toMin = True)
		minFitSize = botFitSize
		if minFitSize > humanFitSize:
			minFitSize = humanFitSize
		
		botClusters = groupFit(minFitSize, botClusters)	
		humanClusters = groupFit(minFitSize, humanClusters)

		botMA = groupMovingAverage(botClusters)
		humanMA = groupMovingAverage(humanClusters)

		botActs = groupActivation(botClusters, botMA)
		humanActs = groupActivation(humanClusters, humanMA)

		botCons = groupContinuous(botClusters, botActs)
		humanCons = groupContinuous(humanClusters, humanActs)

		"""
		for i in range(0, len(botCons)):
			print "bot(" + str(i+1) + ") : shift(" + str(len(botCons[i])) + ")"
			for j in range(0, len(botCons[i])):
				print botCons[i][j][0] + " - " + str(botCons[i][j][1]) + " (" + str(botCons[i][j][3] - botCons[i][j][2]) + ")"
		for i in range(0, len(humanCons)):
			print "human(" + str(i+1) + ") : shift(" + str(len(humanCons[i])) + ")"
			for j in range(0, len(humanCons[i])):
				print humanCons[i][j][0] + " - " + str(humanCons[i][j][1]) + " (" + str(humanCons[i][j][3] - humanCons[i][j][2]) + ")"
		"""

		botPairCons = groupPairContinuous(botCons)
		humanPairCons = groupPairContinuous(humanCons)

		cnt = 1
		for botPairCon in botPairCons:
			print ("bot(" + str(cnt) + ")")
			cnt += 1
			printPairContinuous(botPairCon)
		cnt = 1
		for humanPairCon in humanPairCons:
			print ("human(" + str(cnt) + ")")
			cnt += 1
			printPairContinuous(humanPairCon)
		sys.exit(0)

		for i in range(0, len(botPairCons)):
			scnt = 0
			aFlag = False
			acnt = 0
			for j in range(0, len(botPairCons[i])):
				if botPairCons[i][j][0] == "A":
					if aFlag != True:
						scnt += 1
						aFlag = True
					acnt += 1
				else:
					if aFlag == True:
						aFlag = False
						scnt += 1
			msg = ""
			for j in range(0, len(botPairCons[i])):
				msg += botPairCons[i][j][0]
			print msg
			print "bot(" + str(i+1) + ") : acts(" + str(acnt) + ")"
			print "bot(" + str(i+1) + ") : rest(" + str(len(botPairCons[i]) - acnt) + ")"
			print "bot(" + str(i+1) + ") : shift(" + str(scnt) + ")"
		for i in range(0, len(humanPairCons)):
			scnt = 0
			aFlag = False
			acnt = 0
			for j in range(0, len(humanPairCons[i])):
				if humanPairCons[i][j][0] == "A":
					if aFlag != True:
						scnt += 1
						aFlag = True
					acnt += 1
				else:
					if aFlag == True:
						aFlag = False
						scnt += 1
			msg = ""
			for j in range(0, len(humanPairCons[i])):
				msg += humanPairCons[i][j][0]
			print msg
			print "human(" + str(i+1) + ") : acts(" + str(acnt) + ")"
			print "human(" + str(i+1) + ") : rest(" + str(len(humanPairCons[i]) - acnt) + ")"
			print "human(" + str(i+1) + ") : shift(" + str(scnt) + ")"

    def actRatio(self, time_slot, botRaws, humanRaws):
		botClusters = groupClusteredDensity(time_slot, botRaws)
		humanClusters = groupClusteredDensity(time_slot, humanRaws)

		botFitSize = fitSize(botClusters, toMin = True)
		humanFitSize = fitSize(humanClusters, toMin = True)
		minFitSize = botFitSize
		if minFitSize > humanFitSize:
			minFitSize = humanFitSize
		
		botClusters = groupFit(minFitSize, botClusters)	
		humanClusters = groupFit(minFitSize, humanClusters)

		botMA = groupMovingAverage(botClusters)
		humanMA = groupMovingAverage(humanClusters)

		botActs = groupActivation(botClusters, botMA)
		humanActs = groupActivation(humanClusters, humanMA)

		botCons = groupContinuous(botClusters, botActs)
		humanCons = groupContinuous(humanClusters, humanActs)

		botPairCons = groupPairContinuous(botCons)
		humanPairCons = groupPairContinuous(humanCons)

		botActRatios = groupActRatio(botPairCons)
		humanActRatios = groupActRatio(humanPairCons)

		t = []
		for i in range(0, len(botActRatios)):
			x = []
			for j in range(0, len(botActRatios[i])):
				x.append(j)
			aver = numpy.average(botActRatios[i])
			value = []
			for actRatio in botActRatios[i]:
				value.append(actRatio - aver)
			t.append(Chart.trace_generator(x, value, "lines", "bot(" + str(i+1) + ")_actRatio"))
		for i in range(0, len(humanActRatios)):
			x = []
			for j in range(0, len(humanActRatios[i])):
				x.append(j)
			aver = numpy.average(humanActRatios[i])
			value = []
			for actRatio in humanActRatios[i]:
				value.append(actRatio - aver)
			t.append(Chart.trace_generator(x, value, "lines", "human(" + str(i+1) + ")_actRatio"))

		filepath = self.path + os.sep + "actRatio(" + str(time_slot) + ").html"
		Chart.draw_simpleLine(filepath, t)

		for i in range(0, len(botActRatios)):
			print "bot(" + str(i+1) + ")_std : " + str(numpy.std(botActRatios[i]))
		for i in range(0, len(humanActRatios)):
			print "human(" + str(i+1) + ")_std : " + str(numpy.std(humanActRatios[i]))

    def actChanges(self, timeSlot, botRaws, humanRaws):
		botClusters = groupClusteredDensity(timeSlot, botRaws)
		humanClusters = groupClusteredDensity(timeSlot, humanRaws)

		botFitSize = fitSize(botClusters, toMin = True)
		humanFitSize = fitSize(humanClusters, toMin = True)
		minFitSize = botFitSize
		if minFitSize > humanFitSize:
			minFitSize = humanFitSize

		botClusters = groupFit(minFitSize, botClusters)	
		humanClusters = groupFit(minFitSize, humanClusters)

		botMAs = groupMovingAverage(botClusters)
		humanMAs = groupMovingAverage(humanClusters)

		botActs = groupActivation(botClusters, botMAs)
		humanActs = groupActivation(humanClusters, humanMAs)

		botActNums = groupActivitiesBasedOnTime(botClusters, botActs)
		humanActNums = groupActivitiesBasedOnTime(humanClusters, humanActs)

		t = []
		for i in range(0, len(botActNums)):
			x = []
			for j in range(0, len(botActNums[i])):
				x.append((j+1)*timeSlot)
			t.append(Chart.trace_generator(x, botActNums[i], "lines", "bot(" + str(i+1) + ")_activities"))
		for i in range(0, len(humanActNums)):
			x = []
			for j in range(0, len(humanActNums[i])):
				x.append((j+1)*timeSlot)
			t.append(Chart.trace_generator(x, humanActNums[i], "lines", "human(" + str(i+1) + ")_activities"))

		filepath = self.path + os.sep + "activities(" + str(timeSlot) + ").html"
		Chart.draw_simpleLine(filepath, t)

    def restRatio(self, game, timeSlot, botRaws, humanRaws):
		bS = restRatioSimilarities(timeSlot, botRaws)
		hS = restRatioSimilarities(timeSlot, humanRaws)
		bD = getDeviations(bS)
		hD = getDeviations(hS)
		filepath = self.path + os.sep + game + "_restratio.html"
		Chart.draw_box(filepath, [(bD, "macro"), (hD, "human")], "RestRatio Similarity", "Similarity")

    def budgetForActivities(self, timeSlot, budgetFillTime, maxBudget, fun, botRaws, humanRaws):
		botClusters = groupClusteredDensity(timeSlot, botRaws)
		humanClusters = groupClusteredDensity(timeSlot, humanRaws)

		botFitSize = fitSize(botClusters, toMin = True)
		humanFitSize = fitSize(humanClusters, toMin = True)
		minFitSize = botFitSize
		if minFitSize > humanFitSize:
			minFitSize = humanFitSize
		
		botClusters = groupFit(minFitSize, botClusters)	
		humanClusters = groupFit(minFitSize, humanClusters)

		botMAs = groupMovingAverage(botClusters)
		humanMAs = groupMovingAverage(humanClusters)

		botActs = groupActivation(botClusters, botMAs)
		humanActs = groupActivation(humanClusters, humanMAs)

		botActNums = groupActivitiesBasedOnTime(botClusters, botActs)
		humanActNums = groupActivitiesBasedOnTime(humanClusters, humanActs)

		botBudgets = groupBudgets(botActNums, fun, maxBudget)
		humanBudgets = groupBudgets(humanActNums, fun, maxBudget)

		t = []

    def distributionAnalyzer(self, timeSlot, botRaws, humanRaws):
		botActRatios = getActRatios(timeSlot, botRaws)
		humanActRatios = getActRatios(timeSlot, humanRaws)

		botDistributions = getDistributions(botActRatios, "bot")
		humanDistributions = getDistributions(humanActRatios, "human")

		Chart.draw_line("result/distribution(" + str(timeSlot) + ")", \
			botDistributions + humanDistributions)

    def regionAnalyzerByTime(self, game, raw):
		touches = raw.nodes

		x = []
		y = []
		z = "bot"
		for touch in touches:
			if touch.time < 1280:
				continue
			if touch.time > 1310:
				break
			x.append(touch.time)
			y.append(touch.region)

		Chart.draw_line_marker("result/" + game + "_region", [(x, y, z)], "touch region", "time(s)", "region")

    def regionAnalyzerByContinuous(self, game, timeSlot, botRaws, humanRaws):
		botTimeCons = getTimeContinuouses(timeSlot, botRaws)
		humanTimeCons = getTimeContinuouses(timeSlot, humanRaws)
		cnt = 0

		for times in botTimeCons[0]:
			sTime = times[0]
			eTime = times[1]

			print sTime
			print eTime

			x = []
			y = []
			z = "bot"
			for node in botRaws[0].nodes:
				if node.time >= sTime:
					if node.time >= eTime:
						break
					x.append(node.time)
					y.append(node.region)

			if len(x) >= 5:
				Chart.draw_line_marker("result/" + game + "_frag(" + str(cnt) + ")", [(x, y, z)], "touch region", "time(s)", "region")
				cnt += 1
			if cnt == 6:
				break

    def regionSimilarityByContinuous(self, game, timeSlot, regionSize, botRaws, humanRaws):
		botClusters = getTimeClusters(timeSlot, botRaws)
		humanClusters = getTimeClusters(timeSlot, humanRaws)
		botCons = getTimeContinuousesFromClusters(botClusters)
		humanCons = getTimeContinuousesFromClusters(humanClusters)
		botRegionVectors = getRegionVectorByTimes(regionSize, botClusters, botCons)
		humanRegionVectors = getRegionVectorByTimes(regionSize, humanClusters, humanCons)
		botSimilarities = getRegionSimilarities(regionSize, botRegionVectors)
		humanSimilarities = getRegionSimilarities(regionSize, humanRegionVectors)
		bD = getDeviations(botSimilarities)
		hD = getDeviations(humanSimilarities)

		filepath = self.path + os.sep + game + "_touch.html"
		Chart.draw_box(filepath, [(bD, "macro"), (hD, "human")], "Touch Similarity", "Similarity")

    def regionSimilarityByTime(self, timeSlot, time, regionSize, botRaws, humanRaws):
		botClusters = getTimeClusters(timeSlot, botRaws)
		humanClusters = getTimeClusters(timeSlot, humanRaws)
		
		botCons = []
		for cluster in botClusters:
			endTime = cluster.nodes[-1].endTime
			con = []
			j = 0
			while j < endTime:
				con.append((j, j+time))
				j += time
			botCons.append(con)
		humanCons = []
		for cluster in humanClusters:
			endTime = cluster.nodes[-1].endTime
			con = []
			j = 0
			while j < endTime:
				con.append((j, j+time))
				j += time
			humanCons.append(con)

		botRegionVectors = getRegionVectorByTimes(regionSize, botClusters, botCons)
		humanRegionVectors = getRegionVectorByTimes(regionSize, humanClusters, humanCons)
		botSimilarities = getRegionSimilarities(regionSize, botRegionVectors)
		humanSimilarities = getRegionSimilarities(regionSize, humanRegionVectors)

		data = []
		botStds = []
		for i in range(0, len(botSimilarities)):
			actRatios = []
			for j in range(0, len(botSimilarities[i])):
				actRatios.append(botSimilarities[i][j])
			botStds.append(1.0 - numpy.std(actRatios) / 2)
			print "[" + str(i+1) + "] - " + str(1.0 - numpy.std(actRatios) / 2)
		data.append((botStds, "macro"))

		humanStds = []
		for i in range(0, len(humanSimilarities)):
			actRatios = []
			for j in range(0, len(humanSimilarities[i])):
				actRatios.append(humanSimilarities[i][j])
			humanStds.append(1.0 - numpy.std(actRatios) / 2)
			print "[" + str(i+1) + "] - " + str(1.0 - numpy.std(actRatios) / 2)
		data.append((humanStds, "human"))

		filepath = self.path + os.sep + "Timesimilarity(" + str(timeSlot) + ").html"
		Chart.draw_box(filepath, data, "Similarities", "Similarity")

    def actSeqNum(self, timeSlot, botRaws, humanRaws):
		botClusters = groupClusteredDensity(timeSlot, botRaws)
		humanClusters = groupClusteredDensity(timeSlot, humanRaws)

		botFitSize = fitSize(botClusters, toMin = True)
		humanFitSize = fitSize(humanClusters, toMin = True)
		minFitSize = botFitSize
		if minFitSize > humanFitSize:
			minFitSize = humanFitSize
		
		botClusters = groupFit(minFitSize, botClusters)	
		humanClusters = groupFit(minFitSize, humanClusters)

		botMA = groupMovingAverage(botClusters)
		humanMA = groupMovingAverage(humanClusters)

		botActs = groupActivation(botClusters, botMA)
		humanActs = groupActivation(humanClusters, humanMA)

		botCons = groupContinuous(botClusters, botActs)
		humanCons = groupContinuous(humanClusters, humanActs)

		data = []
		for con in botCons:
			i = 1
			j = 1
			x = [0]
			y = [0]
			while j < len(con) and i <= con[-1][3]:
				x.append(i)
				if i >= con[j][3]:
					y.append(y[-1] + 1)
					j += 2
				else:
					y.append(y[-1])
				i += 1
			z = "macro"
			data.append((x, y, z))
		for con in humanCons:
			i = 1
			j = 1
			x = [0]
			y = [0]
			while j < len(con) and i <= con[-1][3]:
				x.append(i)
				if i >= con[j][3]:
					y.append(y[-1] + 1)
					j += 2
				else:
					y.append(y[-1])
				i += 1
			z = "human"
			data.append((x, y, z))

		Chart.draw_line2("result/actseqnum(" + str(timeSlot) + ")", \
			data, "", "time(s)", "Number of Input Sequence")

    def mixedFeature(self, game, timeSlot, regionSize, botRaws, humanRaws):
		brs = restRatioSimilarities(timeSlot, botRaws)
		hrs = restRatioSimilarities(timeSlot, humanRaws)

		botClusters = getTimeClusters(timeSlot, botRaws)
		humanClusters = getTimeClusters(timeSlot, humanRaws)
		botCons = getTimeContinuousesFromClusters(botClusters)
		humanCons = getTimeContinuousesFromClusters(humanClusters)
		botRegionVectors = getRegionVectorByTimes(regionSize, botClusters, botCons)
		humanRegionVectors = getRegionVectorByTimes(regionSize, humanClusters, humanCons)
		botSimilarities = getRegionSimilarities(regionSize, botRegionVectors)
		humanSimilarities = getRegionSimilarities(regionSize, humanRegionVectors)
		mbS = cosineSimilarity([brs, botSimilarities])
		mhS = cosineSimilarity([hrs, humanSimilarities])
		bD = getDeviations(mbS)
		hD = getDeviations(mhS)

		filepath = self.path + os.sep + game + "_mix.html"
		Chart.draw_box(filepath, [(bD, "macro"), (hD, "human")], "Mixed", "Standard Deviations")

    def restTimeDistribution(self, game, timeSlot, botRaws, humanRaws):
		botDensities = groupClusteredDensity(timeSlot, botRaws)
		botCons = groupContinuous(botDensities)
		botpCons = groupPairContinuous(botCons)

		bottpCon = botpCons[0]
		botrTime = []
		botxTime = []
		for e in bottpCon:
			botrTime.append(e[3] - e[2])
			botxTime.append(e[3])

		humanDensities = groupClusteredDensity(timeSlot, humanRaws)
		humanCons = groupContinuous(humanDensities)
		humanpCons = groupPairContinuous(humanCons)

		humantpCon = humanpCons[4]
		humanrTime = []
		humanxTime = []
		for e in humantpCon:
			humanrTime.append(e[3] - e[2])
			humanxTime.append(e[3])

		minX = botxTime[-1]
		if minX > humanxTime[-1]:
			minX = humanxTime[-1]

		for i in reversed(range(0, len(botxTime))):
			if botxTime[i] > minX:
				botxTime.pop()
				botrTime.pop()
		for i in reversed(range(0, len(humanxTime))):
			if humanxTime[i] > minX:
				humanxTime.pop()
				humanrTime.pop()


		data = [ (botxTime, botrTime, "macro"), (humanxTime, humanrTime, "human") ]
		filepath = self.path + os.sep + game + "_rd.html"
		Chart.draw_line_marker(filepath, data, "distribution", "time", "rest time")

    def restSimOverTime(self, timeSlot, botRaws, humanRaws):
		bC = groupClusteredDensity(timeSlot, botRaws)
		bCon = groupContinuous(bC)
		bP = groupPairContinuous(bCon)
		hC = groupClusteredDensity(timeSlot, humanRaws)
		hCon = groupContinuous(hC)
		hP = groupPairContinuous(hCon)

		data = []
		for tP in bP:
			x = []
			y = []
			for i in range(0, len(tP)):
				rTime = []
				for j in range(0, i+1):
					restTime = float(tP[j][3] - tP[j][2])
					totalTime = float(tP[j][3] - tP[j][0])
					restRatio = restTime / totalTime
					rTime.append(restRatio)
				h = 1.0 - numpy.std(rTime) * 0.5
				x.append(tP[j][3])
				y.append(h)
			data.append([x, y, "macro"])
		for tP in hP:
			x = []
			y = []
			for i in range(0, len(tP)):
				rTime = []
				for j in range(0, i+1):
					restTime = float(tP[j][3] - tP[j][2])
					totalTime = float(tP[j][3] - tP[j][0])
					restRatio = restTime / totalTime
					rTime.append(restRatio)
				h = 1.0 - numpy.std(rTime) * 0.5
				x.append(tP[j][3])
				y.append(h)
			data.append([x, y, "human"])

		filepath = "result/rsimtime.html"
		Chart.draw_line2(filepath, data, "RestRatio Similarity Over Time", "Time(s)", "RestRatio Similarity")

    def touchSimOverTime(self, timeSlot, regionSize, botRaws, humanRaws):
		botClusters = getTimeClusters(timeSlot, botRaws)
		humanClusters = getTimeClusters(timeSlot, humanRaws)
		botCons = getTimeContinuousesFromClusters(botClusters)
		humanCons = getTimeContinuousesFromClusters(humanClusters)
		botRegionVectors = getRegionVectorByTimes(regionSize, botClusters, botCons)
		humanRegionVectors = getRegionVectorByTimes(regionSize, humanClusters, humanCons)
		botSimilarities = getRegionSimilarities(regionSize, botRegionVectors)
		humanSimilarities = getRegionSimilarities(regionSize, humanRegionVectors)

		data = []
		for i in range(0, len(botSimilarities)):
			tP = botSimilarities[i]
			x = []
			y = []
			for j in range(0, len(tP)):
				rTime = []
				for k in range(0, j+1):
					rTime.append(tP[k])
				h = 1.0 - numpy.std(rTime) * 0.5
				x.append(botCons[i][j][1])
				y.append(h)
			data.append([x, y, "macro"])
		for i in range(0, len(humanSimilarities)):
			tP = humanSimilarities[i]
			x = []
			y = []
			for j in range(0, len(tP)):
				rTime = []
				for k in range(0, j+1):
					rTime.append(tP[k])
				h = 1.0 - numpy.std(rTime) * 0.5
				x.append(humanCons[i][j][1])
				y.append(h)
			data.append([x, y, "human"])

		filepath = "result/tsimtime.html"
		Chart.draw_line2(filepath, data, "RestRatio Similarity Over Time", "Time(s)", "RestRatio Similarity")
