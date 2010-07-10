class Printer:
	def __init__(self, level=2):
		self.level = level

	def message(self, string, level):
		if level <= self.level:
			print string
	
	def setLevel(self, level):
		self.level = level
