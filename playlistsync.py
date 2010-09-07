#!/usr/bin/env python

import sys, os, re, shutil
from songfile import SongFile
from progress import ProgressBar
from optparse import OptionParser
from mutagen.mp3 import HeaderNotFoundError
import json
import unicodedata
import warnings
from printer import Printer

cacheDir = os.path.join(os.getcwdu(), 'cache')
if not os.path.exists(cacheDir):
    os.mkdir(cacheDir)

p = Printer()
warnings.simplefilter("ignore", UnicodeWarning)

def sanitize(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore')
    s = re.sub(r'[\/:\?]', '_', s)
    return s

def getMetaData(songPath):
    cachePath = os.path.join(cacheDir, str(abs(hash(songPath))))
    song = SongFile()

    try:
        f = open(cachePath, 'r')
        jsonData = json.load(f)
        f.close()
        # TODO: Eventually we should have these expire after a time
        if jsonData['path'] == songPath:
            song.fromJson(jsonData)
        else:
            # Hash collision !
            # TODO: Do something better about this
            raise LookupError()
    except (LookupError, IOError) as e:
        song.load(songPath)
        f = open(cachePath,'w')
        f.write(song.toJson())
        f.close()
        # Pass any errors farther up

    return song

def main(plistpath, dest, options=None):
    if options:
        flat = options.flat
        delete = options.delete
        pretend = options.pretend

    plist = open(plistpath)
    srcset = set()
    destset = set()

    p.message("Parsing playlist.", 1)

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
        p.message("Playlist is empty!", 1)
        sys.exit()

    p.message("Loading metadata from playlist files.", 1)
    if p.level > 1 and p.level < 4:
        bar = ProgressBar(len(playlistpaths),"numbers")
        bar.draw()
    i = 0
    totalbytes=0

    for path in playlistpaths:
        try:
            song = getMetaData(path)
            totalbytes += os.path.getsize(path)

            srcset.add(song)
        except (OSError, IOError) as e:
            p.message("\nError loading {0}: {1}".format(path, e.strerror), 2)
        i += 1
        if p.level > 1 and p.level < 4:
            bar.update(i)

    p.message("{0} files, {1} MB".format(len(playlistpaths), totalbytes/(1024.0*1024.0)), 2)

    p.message("Loading existing files", 1)
    existingFilePaths = []

    for dirpath, dirnames, filenames in os.walk(dest):
        for path in filenames:
            if path[-3:] == 'mp3':
                fullpath = os.path.join(dirpath, path)
                existingFilePaths.append(fullpath)

    if len(existingFilePaths) > 0:
        p.message("Loading metadata from existing files.", 2)
        if p.level > 1 and p.level < 4:
            bar = ProgressBar(len(existingFilePaths),"numbers")
            bar.draw()
        i = 0

        for path in existingFilePaths:
            try:
                song = getMetaData(path)
                destset.add(song)
            except HeaderNotFoundError:
                # This is when the mp3 file in place is malformed, like when it is
                # only a partial file
                os.remove(path)
            except IOError:
                # Something wierd happened
                p.message("File not found" + path, 2)
            i += 1
            if p.level > 1 and p.level < 4:
                bar.update(i)
    else:
        p.message("No existing files", 3)

    toAdd = srcset - destset
    toDel = destset - srcset

    # we can't just take the intersection, because we need the version from
    # dest
    toCheck = set()
    for song in destset:
        if song in srcset:
            toCheck.add(song)

    # Delete songs that shouldn't be there (if we should delete things)
    if delete and len(toDel) > 0 and not pretend:
        p.message("Deleting songs", 1)
        for song in toDel:
            os.remove(song.mp3path)
    else:
        p.message("Not deleting: delete flag={0}, pretend={1} len(toDel)={2}".format(delete,pretend,len(toDel)),5)

    # Move songs around that are already there, but possibly not in the right
    # place
    first = False
    if len(toCheck) > 0:
        for song in toCheck:
            data = song.data(root=dest)
            data['artist'] = sanitize(data['artist'])
            data['album'] = sanitize(data['album'])
            data['title'] = sanitize(data['title'])
            newFile = ""
            if flat == False:
                artistDir = u"{0[root]}/{0[artist]}".format(data)
                albumDir = artistDir + u"/{0[album]}".format(data)
                newFile = albumDir + u"/{0[track]:0>2} {0[title]}.mp3".format(data)

                if not os.path.exists(artistDir):
                    os.mkdir(artistDir)
                if not os.path.exists(albumDir):
                    os.mkdir(albumDir)
            else:
                newFile = u"{0[root]}/{0[artist]} - {0[album]} - {0[track]:0>2} {0[title]}.mp3".format(data)

            if not song.mp3path == newFile:
                if first:
                    first = False
                    p.message("Organizing old songs", 1)
                if not pretend:
                    shutil.move(song.mp3path, newFile)

    # Copy new songs
    if len(toAdd) > 0:
        p.message("Copying songs", 1)
        if p.level > 1 and p.level < 4:
            bar = ProgressBar(len(toAdd),"numbers")
            bar.draw()
        i = 0

        for song in toAdd:
            data = song.data(root=dest)
            data['artist'] = sanitize(data['artist'])
            data['album'] = sanitize(data['album'])
            data['title'] = sanitize(data['title'])
            newPath = ""
            if flat == False:
                artistDir = u"{0[root]}/{0[artist]}".format(data)
                albumDir = artistDir + u"/{0[album]}".format(data)
                newPath = albumDir + u"/{0[track]:0>2} {0[title]}.mp3".format(data)

                if not os.path.exists(artistDir) and not pretend:
                    os.mkdir(artistDir)
                if not os.path.exists(albumDir) and not pretend:
                    os.mkdir(albumDir)
            else:
                newPath = u"{0[root]}/{0[artist]} - {0[album]} - {0[track]:0>2} {0[title]}.mp3".format(data)

            p.message("Copying {0}".format(newPath), 4)
            if not pretend:
                try:
                    shutil.copyfile(song.mp3path, newPath)
                except IOError as e:
                    p.message("Error copying {0}: {1}".format(newPath, e.strerror), 3)
            i += 1
            if p.level > 1 and p.level < 4:
                bar.update(i)
    else:
        p.message("All songs already there!", 1)

    p.message("\nDone.", 1)


if __name__ == "__main__":
    # Set up the option parser
    parser = OptionParser(usage="usage: %prog [options] playlist destination")
    parser.set_defaults(flat=False, verbosity=2, delete=True, pretend=False)

    parser.add_option("-f", "--flat", action="store_true", dest="flat",
            help="Copies files to a single directory, instead of structured into folders.")
    parser.add_option("-s", "--structured", action="store_false", dest="flat",
            help="Copies files to a structured hierarchy, with folders for artists and albums.")
    parser.add_option("-q", "--quiet", action="store_const", dest="verbosity",
            const=1, help="Gives less output. (Verbosity: 1)")
    parser.add_option("-v", "--verbose", action="store", dest="verbosity",
            help="Set verbosity to a particular level. (Default: 2)")
    parser.add_option("-D", "--no-delete", action="store_false", dest="delete",
            help="Don't delete files that are not described in the playlist.")
    parser.add_option("-d", "--delete", action="store_true", dest="delete",
            help="Delete files that are not described in the playlist. (Default)")
    parser.add_option("-p", "--pretend", action="store_true", dest="pretend",
            help="Delete files that are not described in the playlist. (Default)")

    # Parse options
    options, args = parser.parse_args()
    p.setLevel(int(options.verbosity))

    # Make sure we have enough information
    if len(args) < 2:
        parser.print_help()
        sys.exit()

    # DO IT!
    main(args[0],args[1],options)
