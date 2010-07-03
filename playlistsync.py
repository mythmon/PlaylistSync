#!/usr/bin/env python

import sys, os, re, shutil
from songfile import SongFile
from progress import ProgressBar
from optparse import OptionParser
from mutagen.mp3 import HeaderNotFoundError
import unicodedata

def sanitize(s):
	s = unicodedata.normalize('NFKD', s).encode('ascii','ignore')
	s = re.sub(r'[\/:\?]', '_', s)
	return s

if len(sys.argv) < 3:
	print("Usage " + sys.argv[0] + " playlist destination")
	sys.exit()

parser = OptionParser()
parser.set_defaults(flat=False)
parser.add_option("-f", "--flat", action="store_true", dest="flat", help="Copies files to a single directory, instead of structured into folders.")
parser.add_option("-s", "--structured", action="store_false", dest="flat", help="Copies files to a structured hierarchy, with folders for artists and albums.")
options, args = parser.parse_args()

plistpath = args[0]
dest = args[1]

plist = open(plistpath)
srcset = set()
destset = set()

print "Parsing playlist."

playlistpaths = []

for line in plist:
	if line[0] == '#':
		continue

	if line[-1] == '\n':
		path = line[:-1] # strip the new line
	else:
		path = line

	playlistpaths.append(path)

if len(playlistpaths) == 0:
	print("Playlist is empty!")
	sys.exit()

print "Loading metadata from playlist files."
bar = ProgressBar(len(playlistpaths),"numbers")
bar.draw()
i = 0
totalbytes=0

for path in playlistpaths:
	try:
		song = SongFile()
		song.load(path)
		srcset.add(song)
		totalbytes += os.path.getsize(path)
	except (IOError):
		pass
	i += 1
	bar.update(i)

print "{0} files, {1} MB".format(len(playlistpaths), totalbytes/(1024.0*1024.0))

print "Loading existing files"
existingfiles = []

for dirpath, dirnames, filenames in os.walk(dest):
	for file in filenames:
		if file[-3:] == 'mp3':
			fullpath = os.path.join(dirpath, file)
			existingfiles.append(fullpath)

if len(existingfiles) > 0:
	print "Loading ID3 tags from existing files."
	print len(existingfiles)
	bar = ProgressBar(len(existingfiles),"numbers")
	bar.draw()
	i = 0

	for file in existingfiles:
		try:
			song = SongFile()
			song.load(file)
			destset.add(song)
		except (HeaderNotFoundError):
			os.remove(file)
		i += 1
		bar.update(i)
else:
	print "No existing files"

toAdd = srcset - destset
toDel = destset - srcset

# we can't just take the intersection, because we need the version from dest
toCheck = set()
for song in destset:
	if song in srcset:
		toCheck.add(song)

if len(toAdd) > 0:
	print "Copying songs"
	bar = ProgressBar(len(toAdd),"numbers")
	bar.draw()
	i = 0

	for song in toAdd:
		data = song.data(root=dest)
		data['artist'] = sanitize(data['artist'])
		data['album'] = sanitize(data['album'])
		data['title'] = sanitize(data['title'])
		newFile = ""
		if options.flat == False:
			artistDir = u"{0[root]}/{0[artist]}".format(data)
			albumDir = artistDir + u"/{0[album]}".format(data)
			newFile = albumDir + u"/{0[track]:0>2} {0[title]}.mp3".format(data)

			if not os.path.exists(artistDir):
				os.mkdir(artistDir)
			if not os.path.exists(albumDir):
				os.mkdir(albumDir)
		else:
			newFile = u"{0[root]}/{0[artist]} - {0[album]} - {0[track]:0>2} {0[title]}.mp3".format(data)

		try:
			shutil.copyfile(song.filename, newFile)
		except (IOError):
			print "Error copying {0}".format(newFile)
		i += 1
		bar.update(i)
else:
	print "All songs already there!"

if len(toDel) > 0:
	print "Deleting songs"
	for song in toDel:
		os.remove(song.filename)

if len(toCheck) > 0:
	print "Moving songs"
	for song in toCheck:
		data = song.data(root=dest)
		data['artist'] = sanitize(data['artist'])
		data['album'] = sanitize(data['album'])
		data['title'] = sanitize(data['title'])
		newFile = ""
		if options.flat == False:
			artistDir = u"{0[root]}/{0[artist]}".format(data)
			albumDir = artistDir + u"/{0[album]}".format(data)
			newFile = albumDir + u"/{0[track]:0>2} {0[title]}.mp3".format(data)

			if not os.path.exists(artistDir):
				os.mkdir(artistDir)
			if not os.path.exists(albumDir):
				os.mkdir(albumDir)
		else:
			newFile = u"{0[root]}/{0[artist]} - {0[album]} - {0[track]:0>2} {0[title]}.mp3".format(data)

		if not song.filename == newFile:
			shutil.move(song.filename, newFile)

print
print "Done."
