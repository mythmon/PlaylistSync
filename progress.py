#!/usr/bin/env python

import os, time, sys, math

class ProgressBar:

	def __init__(self, maxValue, style="percent"):
		self.style = style
		self.current = 0
		self.maxValue = maxValue
		_,self.width = os.popen('stty size', 'r').read().split()
		self.width = int(self.width)
		self.firstDraw = True
		if style=="percent":
			# leave space for the sides, the brackets, and the percent
			self.width -= 9
		if style=="plain":
			# leave space for the sides and the brackets
			self.width -= 5
		if style=="numbers":
			# Leave space for the sides, the brackets, and the biggest number
			# The biggest number is xxx/xxx, so numOfDigits*2+1 for the space
			numDigits = math.log10(maxValue)
			self.width -= int(math.ceil(numDigits * 2 + 7))

	def update(self,value,redraw=True):
		self.current = value
		if redraw:
			self.draw()

	templates = {
			'percent': ' [{0}{1}]{2:>3}% ',
			'numbers': ' [{0}{1}] {3}/{4} ',
			'plain': ' [{0}{1}] '
			}

	def draw(self):
		percent = self.current / (self.maxValue * 1.0)
		if percent > 1:
			percent = 1
		stars = int(self.width * percent)
		blanks = self.width - stars
		a = ProgressBar.templates[self.style].format('*'*stars,' '*blanks, int(percent*100), self.current, self.maxValue)
		sys.stdout.write("\r")
		sys.stdout.write(a)
		sys.stdout.flush()

if __name__ == "__main__":
	bar = ProgressBar(5,style="numbers")
	n = 0
	while n <= 5:
		bar.update(n)
		bar.draw()
		n += 1
		time.sleep(1)
	print
