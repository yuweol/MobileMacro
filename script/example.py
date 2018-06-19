#!/usr/bin/env python
import math
import plotly.offline as py
import plotly.graph_objs as go

def fun1(a, b, c, x):
	return a * (x - b) * (x - b) + c

def draw1():
	a = (-1.0) * 100.0 / 4.0
	b = 2.0
	c = 100.0

	x = []
	for i in range(0, 101):
		x.append(4.0/100.0*i)
	y = []
	for i in range(0, 101):
		y.append(fun1(a, b, c, x[i]))

	a = (-1.0) * 100.0 / 9.0
	b = 7.0
	c = 100.0
	for i in range(0, 101):
		x.append(6.0/100.0*i + 4.0)
		y.append(fun1(a, b, c, x[i+100]))

	a = (-1.0) * 100.0 / 4.0
	b = 12.0
	c = 100.0
	for i in range(0, 101):
		x.append(4.0/100.0*i + 10.0)
		y.append(fun1(a, b, c, x[-1]))

	t = go.Scatter(x=x, y=y, mode="lines", name="draw1")
	py.plot([t], filename="result/draw1.html", auto_open=False)

def draw2():
	a = (-1.0) * 100.0 / 4.0
	b = 2.0
	c = 100.0

	x = []
	y = []
	for i in range(0, 101):
		x.append(4.0/100.0*i)
		y.append(fun1(a, b, c, x[-1]))
	
	a = (-1.0) * 100.0 / 9.0
	b = 7.0
	c = 100.0
	for i in range(0, 101):
		x.append(6.0/100.0*i + 4.0)
		y.append(fun1(a, b, c, x[-1]))

	t = go.Scatter(x=x, y=y, mode="lines", name="draw1")
	py.plot([t], filename="result/draw1.html", auto_open=False)

def main():
	draw2()

if __name__ == "__main__":
	main()
