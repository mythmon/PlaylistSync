from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import json
from exceptions import *

CACHE_VERSION = 1

class SongFile:
	# Load id3 info from a file
	def load(self,mp3path):
		data = MP3(mp3path, ID3=EasyID3)
		self.mp3path = mp3path
		# Note, these are lists, not single values.
		self.artist = data['artist']
		self.album = data['album']
		self.title = data['title']
		# extract the track num. ie: '2/14' -> 2
		try:
			self.track = [ int(i.split('/')[0]) for i in data['tracknumber'] ]
		except (KeyError):
			self.track = []

	# make a nice pretty string to print out
	def __repr__(self):
		allArtists = ', '.join(self.artist)
		allAlbums = ', '.join(self.album)
		allTitles = ', '.join(self.title)
		allTracks = ', '.join([str(i) for i in self.track])
		return '"{0} by {1} #{2} on {3}"'.format(allTitles, allArtists, allTracks, allAlbums)

	# Use the hash of all the id3 info combined into a string
	def __hash__(self):
		s = ''.join(self.artist + self.album + self.title + [str(i) for i in self.track])
		return hash(s)

	# The has file that will be used for identifying json snippets
	def jsonHash(self):
		return hash(self.mp3path)

	# Convert to json
	def toJson(self):
		data = self.data()
		j = json.dumps(data)
		return j

	# From json
	def fromJson(self, jsonData):
		if int(jsonData['cache_version']) != CACHE_VERSION:
			print jsonData['cache_version'], CACHE_VERSION
			raise CacheVersionError(jsonData['cache_version'], CACHE_VERSION)

		self.mp3path = jsonData['path']
		self.artist = [jsonData['artist']]
		self.album = [jsonData['album']]
		self.title = [jsonData['title']]
		self.track = [jsonData['track']]

	# ignore the path, just worry about the artist,album,title, etc
	def __eq__(self, other):
		return self.__hash__() == other.__hash__()

	# Generate a dictionary with all our data
	def data(self, root=None, single=True):
		data = {}
		data['path'] = self.mp3path
		data['cache_version'] = CACHE_VERSION
		if root:
			data['root'] = root

		if single:
			data['artist'] = ', '.join(self.artist)
			data['album'] = ', '.join(self.album)
			data['title'] = ', '.join(self.title)
			data['track'] = ', '.join([str(i) for i in self.track])
		else:
			data['artist'] = self.artist
			data['album'] = self.album
			data['title'] = self.title
			data['track'] = self.track

		return data
