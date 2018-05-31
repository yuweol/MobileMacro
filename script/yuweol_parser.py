def readFile(path):
	try:
		with open(path, "rt") as f:
			return f.read()
	except FileNotFoundError:
		print ("[ERROR] File not found (" + path + ")")
		sys.exit(1)
		
def readLine(content):
	lines = []
	for line in content.split("\n"):
		line = line.strip()
		if not line.startswith("["):
			continue
		lines.append(line)
	return lines
	
class ParserNode():
	def __init__(self, raw):
		elements = raw.split()
		if not elements[0].endswith("]"):
			if not elements[1].endswith("]"):
				raise RuntimeError("Unknown rawdata : " + str(raw))
			else:
				elements[0] = "[" + elements[1]
				elements.pop(1)
		self.time = float(elements[0][1:-1])
		self.event = elements[2]
		self.action = elements[3]
		self.value = elements[4]

	def __str__(self):
		return str(self.time) + ", " + self.event + \
			", " + self.action + ", " + self.value

class Parser():
	def __init__(self, path):
		self.nodes = []
		lines = readLine(readFile(path))
		line_size = len(lines)
		
		#Skip last line because this can't be completed because of interrupt while writing.
		for i in range(0, line_size - 1):
			self.nodes.append(ParserNode(lines[i]))
