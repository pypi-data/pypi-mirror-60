#Histogram.py

"""
	Histogram-related functions
"""

#import dependencies
import collections
import matplotlib.pyplt as plt

"""
Histogram - function to compute a histogram
Parameters:
	a 	I/P	image array to compute histogram
"""
def Histogram(a):
	assert not a is None #check image is None

	"""
	In current version, histogram is calcuated with an assumption that bin = 255 
	To build histogram, each pixel value is map to a map-table that key is pixel value and value is the number of pixels
	"""
	
	hist = collections.Counter(a) #mapped pixels to hist
	hist = collections.OrderedDict(hist) #map to sorted ordered

	return hist

"""
showHist - function to print a histogram
Parameters:
	hist 	I/P	computed histogram
"""
def showHist(hist):
	fig, axis = plt.subplot(1, 1)

	axis.bar(hist, width = range(0, 255))
	plt.show() 
