#!/usr/bin/env
from cluster import TimeCluster
from chart import Chart

import os

def clusteredDensity(time_slot, r):
    return TimeCluster(r, time_slot).density()

def fitSize((x1, y1), (x2, y2), toMin=True):
    if toMin:
        if len(x1) > len(x2):
            x1 = x1[:len(x2)]
            y1 = y1[:len(y2)]
        else:
            x2 = x2[:len(x1)]
            y2 = y2[:len(y1)]
    else:
        if len(x1) < len(x2):
            for i in range(0, len(x2) - len(x1)):
                x1.append(None)
                y1.append(None)
        else:
            for i in range(0, len(x1) - len(x2)):
                x2.append(None)
                y2.append(None)
    return (x1, y1), (x2, y2)

def movingAverage(y):
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

def budget(a, y, fun, max_budget):
    b = [max_budget, ]
    factor = 0

    for i in range(1, len(a)):
        if a[i] == 1:
            factor = fun(factor)
            if factor >= max_budget:
                factor = max_budget
            next_budget = b[-1] - y[i] + factor
            if next_budget >= max_budget:
                next_budget = max_budget
            b.append(next_budget)
        else:
            factor = 0
            b.append(b[-1] - y[i])

    return b

class Analyzer():
    def __init__(self, path):
        self.path = path

    def touch_density(self, time_slot, r1, r1_type, r2, r2_type):
        x1, y1 = clusteredDensity(time_slot, r1)
        x2, y2 = clusteredDensity(time_slot, r2)

        (x1, y1), (x2, y2) = fitSize((x1, y1), (x2, y2), toMin=True)

        ma1 = movingAverage(y1)
        ma2 = movingAverage(y2)

        t1 = Chart.trace_generator(x1, y1, "lines", r1_type)
        t2 = Chart.trace_generator(x1, ma1, "lines", r1_type + "_average")
        t3 = Chart.trace_generator(x2, y2, "lines", r2_type)
        t4 = Chart.trace_generator(x2, ma2, "line", r2_type + "_average")

        filepath = self.path + os.sep + "density(" + str(time_slot) + ").html"
        Chart.draw_simpleLine(filepath, [t1, t2, t3, t4])

    def touch_activation(self, time_slot, r1, r1_type, r2, r2_type):
        x1, y1 = clusteredDensity(time_slot, r1)
        x2, y2 = clusteredDensity(time_slot, r2)

        (x1, y1), (x2, y2) = fitSize((x1, y1), (x2, y2), toMin=True)

        ma1 = movingAverage(y1)
        ma2 = movingAverage(y2)

        a1 = activation(y1, ma1)
        a2 = activation(y2, ma2)

        t1 = Chart.trace_generator(x1, a1, "lines", r1_type + "_activation")
        t2 = Chart.trace_generator(x2, a2, "lines", r2_type + "_activation")

        filepath = self.path + os.sep + "activation(" + str(time_slot) + ").html"
        Chart.draw_simpleLine(filepath, [t1, t2])

    def score_rest(self, time_slot, fun, r1, r1_type, r2, r2_type):
        x1, y1 = clusteredDensity(time_slot, r1)
        x2, y2 = clusteredDensity(time_slot, r2)

        (x1, y1), (x2, y2) = fitSize((x1, y1), (x2, y2), toMin=True)

        ma1 = movingAverage(y1)
        ma2 = movingAverage(y2)

        a1 = activation(y1, ma1)
        a2 = activation(y2, ma2)

        s1 = score(a1, fun)
        s2 = score(a2, fun)

        t1 = Chart.trace_generator(x1, s1, "lines", r1_type + "_scorerest")
        t2 = Chart.trace_generator(x2, s2, "lines", r2_type + "_scorerest")

        filepath = self.path + os.sep + "score(" + str(time_slot) + ").html"
        Chart.draw_simpleLine(filepath, [t1, t2])

    def budget(self, time_slot, max_budget, fun, r1, r1_type, r2, r2_type):
        x1, y1 = clusteredDensity(time_slot, r1)
        x2, y2 = clusteredDensity(time_slot, r2)

        (x1, y1), (x2, y2) = fitSize((x1, y1), (x2, y2), toMin=True)

        ma1 = movingAverage(y1)
        ma2 = movingAverage(y2)

        a1 = activation(y1, ma1)
        a2 = activation(y2, ma2)

        b1 = budget(a1, y1, fun, max_budget)
        b2 = budget(a2, y2, fun, max_budget)

        t1 = Chart.trace_generator(x1, b1, "lines", r1_type + "_scorerest")
        t2 = Chart.trace_generator(x2, b2, "lines", r2_type + "_scorerest")

        filepath = self.path + os.sep + "budget(" + str(time_slot) + ").html"
        Chart.draw_simpleLine(filepath, [t1, t2])
