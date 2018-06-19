#!/usr/bin/env python

import plotly.offline as py
import plotly.graph_objs as go

class Chart():
	@staticmethod
	def trace_generator(x, y, mode, name):
		return go.Scatter(x = x, y = y, mode = mode, name = name)

	@staticmethod
	def trace_box(y):
		return go.Box(y = y)

	@staticmethod
	def draw_simpleLine(filename, traces):
		py.plot(traces, filename=filename)

	@staticmethod
	def draw_line(filename, data):
		for e in data:
			if len(e) != 3:
				raise RuntimeError("unvalid input")

		traces = []
		for e in data:
			traces.append(go.Scatter(x = e[0], y = e[1], mode = "markers", name = e[2]))

		if not filename.endswith(".html"):
			filename = filename + ".html"

		py.plot(traces, filename=filename, auto_open=False)

	@staticmethod
	def draw_dots(filename, data):
		for e in data:
			if len(e) != 3:
				raise RuntimeError("unvalid input")

		traces = []
		for e in data:
			traces.append(go.Scatter(x = e[0], y = e[1], mode = "lines + markers", name = e[2]))

		if not filename.endswith(".html"):
			filename = filename + ".html"

		py.plot(traces, filename=filename)

	@staticmethod
	def draw_line2(filename, data, title, x, y):
		for e in data:
			if len(e) != 3:
				raise RuntimeError("unvalid input")

		traces = []
		for e in data:
			traces.append(go.Scatter(x = e[0], y = e[1], mode = "lines", name = e[2]))

		if not filename.endswith(".html"):
			filename = filename + ".html"

		layout = go.Layout(
			title = title,
			titlefont = dict(
					size = 30
			),
			xaxis = dict(
				title = x,
				titlefont = dict(
					size = 30
				)
			),
			yaxis = dict(
				title = y,
				titlefont = dict(
					size = 30
				)
			),
			legend = dict(
				font = dict(
					size = 30
				)
			)
		)

		fig = go.Figure(data = traces, layout = layout)
		py.plot(fig, filename = filename, auto_open = False)
		print filename + " was created"

	@staticmethod
	def draw_box(filename, data, title, y):
		for e in data:
			if len(e) != 2:
				raise RuntimeError("unvalid input")

		traces = []
		for e in data:
			traces.append(go.Box(y = e[0], name = e[1], boxpoints = False))

		if not filename.endswith(".html"):
			filename = filename + ".html"

		layout = go.Layout(
			title = title,
			titlefont = dict(
					size = 30
			),
			yaxis = dict(
				title = y,
				titlefont = dict(
					size = 30
				)
			),
			legend = dict(
				font = dict(
					size = 30
				)
			)
		)
		fig = go.Figure(data = traces, layout = layout)
		py.plot(fig, filename = filename, auto_open = False)
		print filename + " was created."

	@staticmethod
	def draw_line_marker(filename, data, title, x, y):
		for e in data:
			if len(e) != 3:
				raise RuntimeError("unvalid input")

		traces = []
		for e in data:
			traces.append(go.Scatter(x = e[0], y = e[1], mode = "markers", name = e[2]))

		if not filename.endswith(".html"):
			filename = filename + ".html"

		layout = go.Layout(
			title = title,
			titlefont = dict(
					size = 30
			),
			xaxis = dict(
				title = x,
				titlefont = dict(
					size = 30
				)
			),
			yaxis = dict(
				title = y,
				titlefont = dict(
					size = 30
				),
				range = [0, 25]
			),
			legend = dict(
				font = dict(
					size = 30
				)
			)
		)

		fig = go.Figure(data = traces, layout = layout)
		py.plot(fig, filename = filename, auto_open = False)
		print filename + " was created"

