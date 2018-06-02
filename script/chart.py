#!/usr/bin/env python

import plotly.offline as py
import plotly.graph_objs as go

class Chart():
	@staticmethod
	def trace_generator(x, y, mode, name):
		return go.Scatter(x = x, y = y, mode = mode, name = name)

	@staticmethod
	def draw_simpleLine(filename, traces):
		py.plot(traces, filename=filename)
