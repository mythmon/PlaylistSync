PlaylistSync
============

A tool to load a list of songs from a playlist file and copy them intelligently
to a directory.

It will scan the destination, removing any files not listed in the playlist,
and ensuring that any files already in place match the organization pattern
chosen. It will then copy only the files that are not already present to the
destination.


Options
-------

* -f, --flat
Organize files into a flat structure, ie: as "$artist - $album - $tracknum
$title.mp3"

* -s, --structured
Organize files into directories based on artist and album, ie: as
"$artist/$album/$tracknum $title.mp3"
