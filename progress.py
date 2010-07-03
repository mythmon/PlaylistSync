#!/usr/bin/env python
# progress.py

"""A class for drawing a progress bar to the console in various styles."""

import os
import time
import sys
import math

class ProgressBar:

	def __init__(self, maxValue, style="percent"):
		self.style = style
		self.current = 0
		self.maxValue = maxValue
		# Get the width of the current console
		_,self.width = os.popen('stty size', 'r').read().split()
		# It is returned as a string. Fix that.
		self.width = int(self.width)
		self.firstDraw = True
		if style=="percent":
			# [****----] 50%
			# Leave space for the sides (2), the brackets(2), the percent (3)
			# and the space between the brackets and percent (1).
			self.width -= 8
		if style=="plain":
			# [******------]
			# Leave space for the sides (2) and the brackets (2).
			self.width -= 4
		if style=="numbers":
			# [***---] 25/50
			# The biggest number is xxx/xxx, so numOfDigits*2+1 for the numbers
			# then 2 more for spaces on either side of the bar, 2 for the
			# brackets.
			numDigits = math.ceil(math.log10(maxValue))
			self.width -= int(numDigits * 2 + 5)

	"""Update the value of the progress bar, and by default redraw it."""
	def update(self,value,redraw=True):
		self.current = value
		if redraw:
			self.draw()

	templates = {
			'percent': ' [{0}{1}]{2:>3}% ',
			'numbers': ' [{0}{1}]{3}/{4} ',
			'plain'  : ' [{0}{1}] '
		}

	"""Draw the progress bar to the screen in the specifed style."""
	def draw(self):
		percent = self.current / (self.maxValue * 1.0)
		if percent > 1:
			percent = 1
		stars = int(self.width * percent)
		blanks = self.width - stars

		bar = ProgressBar.templates[self.style].format('*'*stars, ' '*blanks,
				int(percent*100), self.current, self.maxValue)

		# Reset the cursor to the beginning of the line
		sys.stdout.write("\r")
		# Write over the old progress bar
		sys.stdout.write(bar)
		# Refresh the console
		sys.stdout.flush()

"""Some testing/demo code."""
if __name__ == "__main__":
	bar = ProgressBar(50,style="plain")
	n = 0
	while n <= 50:
		bar.update(n)
		bar.draw()
		n += 1
		time.sleep(0.05)
	print
	bar = ProgressBar(50,style="percent")
	n = 0
	while n <= 50:
		bar.update(n)
		bar.draw()
		n += 1
		time.sleep(0.05)
	print
	bar = ProgressBar(50,style="numbers")
	n = 0
	while n <= 50:
		bar.update(n)
		bar.draw()
		n += 1
		time.sleep(0.05)
	print
