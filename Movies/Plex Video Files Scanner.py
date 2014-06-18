#
# Copyright (c) 2011 Plex Development Team. All rights reserved.
#
import re, os, os.path
import Media, VideoFiles, Stack

# Scans through files, and add to the media list.
def Scan(path, files, mediaList, subdirs, language=None, root=None):
  
  # Just look for video files.
  VideoFiles.Scan(path, files, mediaList, subdirs, root)

  # Add them all.
  for i in files:
    name, year = VideoFiles.CleanName(os.path.basename(i))
    movie = Media.Movie(name, year)
    movie.parts.append(i)
    mediaList.append(movie)
