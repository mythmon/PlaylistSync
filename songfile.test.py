#!/usr/bin/env python

from songfile import SongFile
import json

mp3Path = "/home/mike/Music/Gorillaz/Demon Days/03 Kids With Guns.mp3"
songFile = SongFile()
songFile.load(mp3Path)
print "songFile"
print songFile
print hash(songFile)
print songFile.jsonHash()
print

jsonStr = songFile.toJson()
print "jsonStr"
print jsonStr
print

songFile2 = SongFile()
songFile2.fromJson(jsonStr)
print "songFile2"
print songFile2
print songFile2.artist
print hash(songFile2)
print songFile2.jsonHash()
