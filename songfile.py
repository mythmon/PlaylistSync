from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

class SongFile:
	def __init__(self, file):
		data = MP3(file, ID3=EasyID3)
		self.artist = data['artist']
		self.album = data['album']
		self.title = data['title']
		# extract the track num. ie: '2/14' -> 2
		try:
			self.track = [ int(i.split('/')[0]) for i in data['tracknumber'] ]
		except (KeyError):
			self.track = []
		self.filename = file

	def __repr__(self):
		allArtists = ', '.join(self.artist)
		allAlbums = ', '.join(self.album)
		allTitles = ', '.join(self.title)
		allTracks = ', '.join([str(i) for i in self.track])
		return '"{0} by {1} #{2} on {3}"'.format(allTitles, allArtists, allTracks, allAlbums)

	def __hash__(self):
		s = ''.join(self.artist + self.album + self.title + [str(i) for i in self.track])
		return hash(s)

	def __eq__(self, other):
		return self.__hash__() == other.__hash__()

	def data(self, root=None, single=True):
		data = {}
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
