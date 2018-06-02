
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
	
class token_manager():
	def __init__(self, path):
		self.tokens = []
		lines = readLine(readFile(path))
		line_size = len(lines)
		for i in range(0, line_size - 1):
			self.tokens.append(token(lines[i]))
			
	def size(self):
		return len(self.tokens)
		
	def get(self, index):
		return self.tokens[index]

class token():
		
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
			
	def getTime(self):
		return self.time
		
	def getAction(self):
		return self.action
	
	def getValue(self):
		return self.value